/*
 * firefly - the NoC Simulator
 *
 * (C)  2014 by the Colorado State University
 * For the complete list of authors refer to file ../doc/AUTHORS.txt
 * For the license applied to these sources refer to file ../doc/LICENSE.txt
 *
 * This file contains the implementation of the Firefly Photonic Network-on-Chip
 */

#include "fireflyNoC.h"

/* This method implements concentrator which has a photonic interface 
 * that connects to 8x8 SWMR waveguide crossbar 
 */

void fireflyNoC::buildConcentrators()
{
  for(int i = 0; i < ((fireflyGlobalParams::mesh_dim_x * fireflyGlobalParams::mesh_dim_y) / 4) ; i++)
  {
    Concentrators[i] = new fireflyConcentrator(sc_gen_unique_name("Firefly_Con_"), PStats);
    // Determine cluster and assembley IDs of concentrator
    int cluster_id = getClusterId(i, (fireflyGlobalParams::mesh_dim_x * fireflyGlobalParams::mesh_dim_y));
    int assembly_id = getAssemblyId(i, (fireflyGlobalParams::mesh_dim_x * fireflyGlobalParams::mesh_dim_y));

    Concentrators[i] -> configure(i, cluster_id, assembly_id);
    // Connect clock and reset to concentrator 
    Concentrators[i] -> faster_clock(faster_clock);
    Concentrators[i] -> clock(clock);
    Concentrators[i] -> reset(reset);
    // Loop that maps receive and transmission signals to concentrator ports
    for(int k = 0 ; k < 5 ; k++)
    {
      // Map Rx signals
      Concentrators[i] -> req_rx[k] (req_from_core[i][k]);
      Concentrators[i] -> flit_rx[k] (flit_from_core[i][k]);
      Concentrators[i] -> ack_rx[k] (ack_to_core[i][k]);

      // Map Tx signals
      Concentrators[i] -> req_tx[k] (req_to_core[i][k]);
      Concentrators[i] -> flit_tx[k] (flit_to_core[i][k]);
      Concentrators[i] -> ack_tx[k] (ack_from_core[i][k]);      
    }
    
  }

  for(int i = 0; i < (fireflyGlobalParams::mesh_dim_x * fireflyGlobalParams::mesh_dim_y) ; i++)
  {
    // Processing Element pin assignments
    
    pe[i] = new fireflyProcessingElement(sc_gen_unique_name("fireflyProcessingElement_"), PStats,  arg_pir, arg_por);
    pe[i] -> local_id = i;
    pe[i] -> traffic_table = &gttable;	// Needed to choose destination
    pe[i] -> never_transmit = (gttable.occurrencesAsSource(i) == 0);    
    
    int concentrator_id = getConcentratorId(i , (fireflyGlobalParams::mesh_dim_x * fireflyGlobalParams::mesh_dim_y));
    int core_index      = getCoreIndex(i);
    if((fireflyGlobalParams::mesh_dim_x * fireflyGlobalParams::mesh_dim_y) == 64)
    assert(concentrator_id <= 15);
    else
    assert(concentrator_id <= 64);
    assert(core_index <= 3);

    //cout << i << " core_id " << core_index << " core_index " << concentrator_id << " concentrator_id " << endl;
    pe[i]->clock(clock);
    pe[i]->reset(reset);

    pe[i]-> req_rx(req_to_core[concentrator_id][core_index]);
    pe[i]-> flit_rx(flit_to_core[concentrator_id][core_index]);
    pe[i]-> ack_rx(ack_from_core[concentrator_id][core_index]);

    pe[i]-> req_tx(req_from_core[concentrator_id][core_index]);
    pe[i]-> flit_tx(flit_from_core[concentrator_id][core_index]);
    pe[i]-> ack_tx(ack_to_core[concentrator_id][core_index]); 

    referenceNodes[concentrator_id][core_index] = pe[i];    
  }  
}

//---------------------------------------------------------------------------
/* This method implements Mesh NoC within each concentrator 
 */
void fireflyNoC::buildMesh()
{
  // Check for routing table availability
  if (fireflyGlobalParams::routing_algorithm == ROUTING_TABLE_BASED)
  assert(grtable.load(fireflyGlobalParams::routing_table_filename));

  // Check for traffic table availability
  if (fireflyGlobalParams::traffic_distribution == TRAFFIC_TABLE_BASED)
  assert(gttable.load(fireflyGlobalParams::traffic_table_filename));

  // Create the mesh as a matrix of tiles
  int running_index = ((fireflyGlobalParams::mesh_dim_x * fireflyGlobalParams::mesh_dim_y) == 64) ? 4 : 8;
  for (int i = 0; i < (fireflyGlobalParams::mesh_dim_x  / 2 ); i++)
  {
    for (int j = 0; j < (fireflyGlobalParams::mesh_dim_x  / 2 ); j++)
    {
    // Create the single Tile with a proper name
    int router_id = j * (fireflyGlobalParams::mesh_dim_x  / 2 ) + i;
    int cluster_id = getClusterId(router_id, (fireflyGlobalParams::mesh_dim_x * fireflyGlobalParams::mesh_dim_y));
    int assembly_id = getAssemblyId(router_id, (fireflyGlobalParams::mesh_dim_x * fireflyGlobalParams::mesh_dim_y));    

    t[i][j] = new fireflyTile(sc_gen_unique_name("fireflyTile_"), referenceNodes[router_id], PStats);
    
    //assert(router_id <= 15);
    // Tell to the router its coordinates
    t[i][j]->r->configure(router_id,
    cluster_id,
    assembly_id,
    fireflyGlobalParams::stats_warm_up_time,
    fireflyGlobalParams::buffer_depth,
    grtable);

    // Map clock and reset
    t[i][j]->clock(clock);
    t[i][j]->drain_clock(drain_clock);
    t[i][j]->reset(reset);
    t[i][j]->faster_clock(faster_clock);
    t[i][j]->p_flit_swmr_tx(r_swmr_flit[router_id]);
    
    vector<int> assembly_ids = getListeners(router_id , (fireflyGlobalParams::mesh_dim_x * fireflyGlobalParams::mesh_dim_y));
    assert(assembly_ids.size() >0 && assembly_ids.size() < 8 );
    
    for(int k = 0 ; k < assembly_ids.size() ; k++)
    {
      //if(router_id == 50)
      //cout << assembly_ids[k] << " assembly_ids[k] " << endl;
      t[i][j]->p_flit_swmr_rx[k](r_swmr_flit[assembly_ids[k]]);
    }
    

    // Map Rx signals
    t[i][j]->req_rx[DIRECTION_NORTH] (req_to_south[i][j]);
    t[i][j]->flit_rx[DIRECTION_NORTH] (flit_to_south[i][j]);
    t[i][j]->ack_rx[DIRECTION_NORTH] (ack_to_north[i][j]);

    t[i][j]->req_rx[DIRECTION_EAST] (req_to_west[i + 1][j]);
    t[i][j]->flit_rx[DIRECTION_EAST] (flit_to_west[i + 1][j]);
    t[i][j]->ack_rx[DIRECTION_EAST] (ack_to_east[i + 1][j]);

    t[i][j]->req_rx[DIRECTION_SOUTH] (req_to_north[i][j + 1]);
    t[i][j]->flit_rx[DIRECTION_SOUTH] (flit_to_north[i][j + 1]);
    t[i][j]->ack_rx[DIRECTION_SOUTH] (ack_to_south[i][j + 1]);

    t[i][j]->req_rx[DIRECTION_WEST] (req_to_east[i][j]);
    t[i][j]->flit_rx[DIRECTION_WEST] (flit_to_east[i][j]);
    t[i][j]->ack_rx[DIRECTION_WEST] (ack_to_west[i][j]);
    
    t[i][j]->req_rx[DIRECTION_LOCAL] (req_to_core[router_id][4]);
    t[i][j]->flit_rx[DIRECTION_LOCAL] (flit_to_core[router_id][4]);
    t[i][j]->ack_rx[DIRECTION_LOCAL] (ack_from_core[router_id][4]);    

    // Map Tx signals
    t[i][j]->req_tx[DIRECTION_NORTH] (req_to_north[i][j]);
    t[i][j]->flit_tx[DIRECTION_NORTH] (flit_to_north[i][j]);
    t[i][j]->ack_tx[DIRECTION_NORTH] (ack_to_south[i][j]);

    t[i][j]->req_tx[DIRECTION_EAST] (req_to_east[i + 1][j]);
    t[i][j]->flit_tx[DIRECTION_EAST] (flit_to_east[i + 1][j]);
    t[i][j]->ack_tx[DIRECTION_EAST] (ack_to_west[i + 1][j]);

    t[i][j]->req_tx[DIRECTION_SOUTH] (req_to_south[i][j + 1]);
    t[i][j]->flit_tx[DIRECTION_SOUTH] (flit_to_south[i][j + 1]);
    t[i][j]->ack_tx[DIRECTION_SOUTH] (ack_to_north[i][j + 1]);

    t[i][j]->req_tx[DIRECTION_WEST] (req_to_west[i][j]);
    t[i][j]->flit_tx[DIRECTION_WEST] (flit_to_west[i][j]);
    t[i][j]->ack_tx[DIRECTION_WEST] (ack_to_east[i][j]);

    t[i][j]->req_tx[DIRECTION_LOCAL] (req_from_core[router_id][4]);
    t[i][j]->flit_tx[DIRECTION_LOCAL] (flit_from_core[router_id][4]);
    t[i][j]->ack_tx[DIRECTION_LOCAL] (ack_to_core[router_id][4]);    

    // Map buffer level signals (analogy with req_tx/rx port mapping)
    t[i][j]->free_slots[DIRECTION_NORTH] (free_slots_to_north[i][j]);
    t[i][j]->free_slots[DIRECTION_EAST] (free_slots_to_east[i + 1][j]);
    t[i][j]->free_slots[DIRECTION_SOUTH] (free_slots_to_south[i][j + 1]);
    t[i][j]->free_slots[DIRECTION_WEST] (free_slots_to_west[i][j]);

    t[i][j]->free_slots_neighbor[DIRECTION_NORTH] (free_slots_to_south[i][j]);
    t[i][j]->free_slots_neighbor[DIRECTION_EAST] (free_slots_to_west[i + 1][j]);
    t[i][j]->free_slots_neighbor[DIRECTION_SOUTH] (free_slots_to_north[i][j + 1]);
    t[i][j]->free_slots_neighbor[DIRECTION_WEST] (free_slots_to_east[i][j]);

    // Map no operation signals (NoP)  
    t[i][j]->NoP_data_out[DIRECTION_NORTH] (NoP_data_to_north[i][j]);
    t[i][j]->NoP_data_out[DIRECTION_EAST] (NoP_data_to_east[i + 1][j]);
    t[i][j]->NoP_data_out[DIRECTION_SOUTH] (NoP_data_to_south[i][j + 1]);
    t[i][j]->NoP_data_out[DIRECTION_WEST] (NoP_data_to_west[i][j]);

    t[i][j]->NoP_data_in[DIRECTION_NORTH] (NoP_data_to_south[i][j]);
    t[i][j]->NoP_data_in[DIRECTION_EAST] (NoP_data_to_west[i + 1][j]);
    t[i][j]->NoP_data_in[DIRECTION_SOUTH] (NoP_data_to_north[i][j + 1]);
    t[i][j]->NoP_data_in[DIRECTION_WEST] (NoP_data_to_east[i][j]);
    }
  }

  // dummy fireflyNoP_data structure
  fireflyNoP_data tmp_NoP;

  tmp_NoP.sender_id = NOT_VALID;

  for (int i = 0; i < DIRECTIONS; i++)
  {
    tmp_NoP.channel_status_neighbor[i].free_slots = NOT_VALID;
    tmp_NoP.channel_status_neighbor[i].available = false;
  }

  // Clear signals for borderline nodes
  for (int i = 0; i <= 4; i++)
  {
    req_to_south[i][0] = 0;
    ack_to_north[i][0] = 0;
    req_to_north[i][4] = 0;
    ack_to_south[i][4] = 0;

    free_slots_to_south[i][0].write(NOT_VALID);
    free_slots_to_north[i][4].write(NOT_VALID);

    NoP_data_to_south[i][0].write(tmp_NoP);
    NoP_data_to_north[i][4].write(tmp_NoP);
  }

  for (int j = 0; j <= 4; j++)
  {
    req_to_east[0][j] = 0;
    ack_to_west[0][j] = 0;
    req_to_west[4][j] = 0;
    ack_to_east[4][j] = 0;

    free_slots_to_east[0][j].write(NOT_VALID);
    free_slots_to_west[4][j].write(NOT_VALID);

    NoP_data_to_east[0][j].write(tmp_NoP);
    NoP_data_to_west[4][j].write(tmp_NoP);
  }

}

//---------------------------------------------------------------------------
fireflyTile *fireflyNoC::searchNode(const int id) const
{
  for (int i = 0; i < 4; i++)
  for (int j = 0; j < 4; j++)
    if (t[i][j]->r->local_id == id)
    return t[i][j];
}
