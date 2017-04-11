/*
* firefly - the NoC Simulator
*
* (C) 2014 by the Colorado State University
* For the complete list of authors refer to file ../doc/AUTHORS.txt
* For the license applied to these sources refer to file ../doc/LICENSE.txt
*
* This file represents the overview of Firefly PNoC architecure
*/

#ifndef __FIREFLYNOC_H__
#define __FIREFLYNOC_H__

#include <systemc.h>
#include "fireflyTile.h"
#include "fireflyGlobalRoutingTable.h"
#include "fireflyGlobalTrafficTable.h"
#include "fireflyPhotonicStats.h"
#include "fireflyConcentrator.h"
#include "fireflyProcessingElement.h"


using namespace std;

SC_MODULE(fireflyNoC)
{

  // I/O Ports
  sc_in_clk clock;		// The input clock for the NoC
  sc_in_clk faster_clock;  
  sc_in_clk drain_clock;
  sc_in < bool > reset;	// The reset signal for the NoC

  // Signals
  sc_signal <bool> req_to_east[MAX_STATIC_DIM + 1][MAX_STATIC_DIM + 1];
  sc_signal <bool> req_to_west[MAX_STATIC_DIM + 1][MAX_STATIC_DIM + 1];
  sc_signal <bool> req_to_south[MAX_STATIC_DIM + 1][MAX_STATIC_DIM + 1];
  sc_signal <bool> req_to_north[MAX_STATIC_DIM + 1][MAX_STATIC_DIM + 1];

  sc_signal <bool> ack_to_east[MAX_STATIC_DIM + 1][MAX_STATIC_DIM + 1];
  sc_signal <bool> ack_to_west[MAX_STATIC_DIM + 1][MAX_STATIC_DIM + 1];
  sc_signal <bool> ack_to_south[MAX_STATIC_DIM + 1][MAX_STATIC_DIM + 1];
  sc_signal <bool> ack_to_north[MAX_STATIC_DIM + 1][MAX_STATIC_DIM + 1];

  sc_signal <fireflyFlit> flit_to_east[MAX_STATIC_DIM + 1][MAX_STATIC_DIM + 1];
  sc_signal <fireflyFlit> flit_to_west[MAX_STATIC_DIM + 1][MAX_STATIC_DIM + 1];
  sc_signal <fireflyFlit> flit_to_south[MAX_STATIC_DIM + 1][MAX_STATIC_DIM + 1];
  sc_signal <fireflyFlit> flit_to_north[MAX_STATIC_DIM + 1][MAX_STATIC_DIM + 1];

  sc_signal <int> free_slots_to_east[MAX_STATIC_DIM + 1][MAX_STATIC_DIM + 1];
  sc_signal <int> free_slots_to_west[MAX_STATIC_DIM + 1][MAX_STATIC_DIM + 1];
  sc_signal <int> free_slots_to_south[MAX_STATIC_DIM + 1][MAX_STATIC_DIM + 1];
  sc_signal <int> free_slots_to_north[MAX_STATIC_DIM + 1][MAX_STATIC_DIM + 1];

  // NoP
  sc_signal <fireflyNoP_data> NoP_data_to_east[MAX_STATIC_DIM][MAX_STATIC_DIM];
  sc_signal <fireflyNoP_data> NoP_data_to_west[MAX_STATIC_DIM][MAX_STATIC_DIM];
  sc_signal <fireflyNoP_data> NoP_data_to_south[MAX_STATIC_DIM][MAX_STATIC_DIM];
  sc_signal <fireflyNoP_data> NoP_data_to_north[MAX_STATIC_DIM][MAX_STATIC_DIM];

  // Matrix of tiles
  fireflyTile *t[MAX_STATIC_DIM][MAX_STATIC_DIM];
  fireflyPStats          &PStats;
  fireflyConcentrator  *Concentrators[64]; // hard-coded
  fireflyProcessingElement *pe[256];	                // Processing Element instance
  fireflyProcessingElement *referenceNodes[64][4]; // do not change the number here
  
  
  sc_signal <bool>         req_to_core[MAX_STATIC_DIM + 1][MAX_STATIC_DIM + 1];
  sc_signal <bool>         req_from_core[MAX_STATIC_DIM + 1][MAX_STATIC_DIM + 1];
  sc_signal <fireflyFlit>  flit_to_core[MAX_STATIC_DIM + 1][MAX_STATIC_DIM + 1];
  sc_signal <fireflyFlit>  flit_from_core[MAX_STATIC_DIM + 1][MAX_STATIC_DIM + 1];
  sc_signal <bool>         ack_to_core[MAX_STATIC_DIM + 1][MAX_STATIC_DIM + 1];
  sc_signal <bool>         ack_from_core[MAX_STATIC_DIM + 1][MAX_STATIC_DIM + 1];
  
  sc_signal <fireflyFlit>  r_swmr_flit[MAX_STATIC_DIM + 1];
  

  // Global tables
  fireflyGlobalRoutingTable grtable;
  fireflyGlobalTrafficTable gttable;
  char*        arg_pir;
  char*        arg_por;
  void buildConcentrators();
  // Constructor

  fireflyNoC(sc_module_name name , fireflyPStats &_PStats, char* arg_vet[]):
  PStats(_PStats)
  {
    arg_pir = arg_vet[1];
    arg_por = arg_vet[2];    
    // Build the concentrators
    buildConcentrators();

    // Build the external concentrators
    buildMesh();
  }

  // Support methods
  fireflyTile *searchNode(const int id) const;

  private:
  void buildMesh();


};

#endif
