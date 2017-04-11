"""
 * Thread migration scheme that use Predictive Dynamic Thermal Managment
 *
 * (C)  2015 by the Colorado State University
 *
 * This file contains a thread migration scheme that employs linear regression 
   based prediction mechanism towards predicting future temperature. Once temeprature 
   of a core exceeds thermal thershold then this thread migration scheme migrate thread form 
   that core to coolest free core. 
"""
import numpy as np
import csv
from subprocess import call
import sys

benchmark = [str(sys.argv[0])]
bt = int(sys.argv[1])
tc = sys.argv[2:2+bt]
#print tc
threads_count =tc 
#threads_count =[str(sys.argv[2]), str(sys.argv[4]), str(sys.argv[6])]
file_path = '/home/vineel/sniper-6.0/benchmarks/Power_Inst_trace_PARSEC/'
chip_core = '64'
# Loop that iterates over splash2 and PARSEC benchmarks
for aplication in (benchmark):
	# Loop that iterates over different thread counts of a benchmark 
	for threads in (threads_count):
		f_results.write("Benhcmark: %s, Thread: %s \n" %(benchmark, threads))
		# Loading IPC trace and power trace in 2D array
		#--------------------------------------------------------------------------------------------
		# Loading IPC trace
		current_benchmark_Inst_trace_path = file_path+aplication+'_'+chip_core+'_'+threads+'/ipc_trace.csv'
		f_i = open(current_benchmark_Inst_trace_path, 'rb')
		rows_i = list(csv.reader(f_i)) # Loading rows of IPC traces
		c_i = [[0 for x in range(64)] for x in range(len(rows_i)-1)] # Intialize a 2D array to store IPC trace
		# Nested loop that loads IPC tarce into an array
		for i in range (1, len(rows_i)):
			t = rows_i[i][0].split()
			for j in range (1, len(t)):
				c_i[i-1][j-1] = t[j]
		#print "IPC trace :",len(c_i),len(c_i[0])		
		#--------------------------------------------------------------------------------------------
		# Loading power trace 
		current_benchmark_power_path =  file_path+aplication+'_'+chip_core+'_'+threads+'/Power_trace.csv'
		f_p = open(current_benchmark_power_path, 'rb')
		rows = list(csv.reader(f_p))   # Loading rows of power traces
		c = [[0 for x in range(64)] for x in range(len(rows))]
		# Nested loop that loads power tarce into an array
		#print "Power trace :",len(rows)
		for i in range (len(rows)):
			t = rows[i][0].split()
			for j in range (len(t)-1):
				c[i][j] = t[j+1]
		#print "Power trace :",len(c),len(c[0])	
		f_i.close()
		f_p.close()
		#--------------------------------------------------------------------------------------------
		# Updating IPC and 	Power traces as per intial thread mapping. 
		# Intial thread mapping is done for 64, 48, 32, and 16 threads of a benchamrk application
		c_i_u = [[0 for x in range(64)] for x in range(len(c_i))] # Array that stores updated instruction traces 
		c_p_u = [[0 for x in range(64)] for x in range(len(c))]   # Array that stores updated power traces
		power_core = 1
		simple_core = int(threads) + 1
		# Loop that iterates over all that cores for intial thread assignment
		for core in range (0, 64):
			if (core == 0):
				#Mapping the thread that executes serial portion of the bnechmark to core 0 
				#print core, core
				for i in range (0, len(c_i)):
					c_i_u[i][core] = c_i[i][core]
					c_p_u[i][core] = c[i][core]	
			else:				
				#Thread mapping when thread count is 64
				if (threads == '64'):
					for i in range (0, len(c_i)):
						c_i_u[i][core] = c_i[i][core]
						c_p_u[i][core] = c[i][core]	
				#Thread mapping when thread count is 16
				if (threads == '16'):
					if((core//8) % 2 == 0):
						if (core%2 == 1):
							#print core, power_core				
							for i in range (0, len(c_i)):
								c_i_u[i][core] = c_i[i][power_core]
								c_p_u[i][core] = c[i][power_core]
							power_core += 1
						else:
							#print core, simple_core
							for i in range (0, len(c_i)):
								c_i_u[i][core] = c_i[i][simple_core]
								c_p_u[i][core] = c[i][simple_core]
							simple_core += 1
					else:
						#print core, simple_core
						for i in range (0, len(c_i)):
								c_i_u[i][core] = c_i[i][simple_core]
								c_p_u[i][core] = c[i][simple_core]
						simple_core += 1
				 #Thread mapping when thread count is 32
				if (threads == '32'):
					if((core//8) % 2 == 0):
						if (core%2 == 1):
							#print core, power_core				
							for i in range (0, len(c_i)):
								c_i_u[i][core] = c_i[i][power_core]
								c_p_u[i][core] = c[i][power_core]
							power_core = power_core + 1
						else:
							#print core, simple_core
							for i in range (0, len(c_i)):
								c_i_u[i][core] = c_i[i][simple_core]
								c_p_u[i][core] = c[i][simple_core]
							simple_core = simple_core + 1
					else:
						if (core%2 == 0):
							#print core, power_core				
							for i in range (0, len(c_i)):
								c_i_u[i][core] = c_i[i][power_core]
								c_p_u[i][core] = c[i][power_core]
							power_core = power_core + 1
						else:
							#print core, simple_core
							for i in range (0, len(c_i)):
								c_i_u[i][core] = c_i[i][simple_core]
								c_p_u[i][core] = c[i][simple_core]
							simple_core = simple_core + 1	
				#Thread mapping when thread count is 48
				if (threads == '48'):
					if((core//8) % 2 == 0):
						if (core%2 == 1):
							#print core, power_core					
							for i in range (0, len(c_i)):
								c_i_u[i][core] = c_i[i][power_core]
								c_p_u[i][core] = c[i][power_core]
							power_core = power_core + 1
						else:
							#print core, simple_core	
							for i in range (0, len(c_i)):
								c_i_u[i][core] = c_i[i][simple_core]
								c_p_u[i][core] = c[i][simple_core]
							simple_core = simple_core + 1
					else:
						#print core, power_core	
						for i in range (0, len(c_i)):
								c_i_u[i][core] = c_i[i][power_core]
								c_p_u[i][core] = c[i][power_core]
						power_core = power_core + 1	
		# End of intilization process before starting to migrate threads
		############################################################################################################################
		# Code that is used to check erros of the intilization process
		#f_temp = open('Power_updated.csv','w')
		#for i in range (0, len(c_i_u)):
			#for core in range (0,64):
				#f_temp.write("%s " %(c_p_u[i][core]))
			#f_temp.write("\n")
		#f_temp.close()
		# End of code that is used to check erros of the intilization process
		############################################################################################################################
		#Code that do thread migration
		#Initialize number of iterations based on the thread count of aplication
		if (threads == '16'):
			Iterations = int(sys.argv[len(sys.argv)-1])
			f_results.write("Number of iterations: %d \n" %(Iterations))
		elif (threads == '32'):
			Iterations = int(sys.argv[len(sys.argv)-2])
			f_results.write("Number of iterations: %d \n" %(Iterations))
		elif (threads == '48'):
			Iterations = int(sys.argv[len(sys.argv)-3])
			f_results.write("Number of iterations: %d \n" %(Iterations))
		elif (threads == '64'):
			Iterations = 0 #len(c)/10
			f_results.write("Number of iterations: %d \n" %(Iterations))
		current_interval = 10 # Number of traces processed for epoc, currently 10 which is 1ms epc size
		f_results.write("Current Epoc size (In ms): %d \n" %(current_interval/10))
		#--------------------------------------------------------------------------------------------
		# Generate layer wise floor plan files using power traces for 3D-ICE tool to generate temeprature traces 
		current_benchmark_E_floor_plan_path = file_path+aplication+'_'+chip_core+'_'+threads+'/Power_trace_migration_layout_Electrical.flp'
		current_benchmark_P1_floor_plan_path = file_path+aplication+'_'+chip_core+'_'+threads+'/Power_trace_migration_layout_Photonic1.flp'
		current_benchmark_P2_floor_plan_path = file_path+aplication+'_'+chip_core+'_'+threads+'/Power_trace_migration_layout_Photonic2.flp'
		# Creating three input files for 3D-ICE tool one for eletrical layer floor plan 
		# and the other two for photonic layer floor plans 
		f1 = open(current_benchmark_E_floor_plan_path,'w')
		f2 = open(current_benchmark_P1_floor_plan_path,'w')
		f3 = open(current_benchmark_P2_floor_plan_path,'w')
		# Nested loops that copies power traces from the updated array (c_p_u) to the floor plan files 
		for core in range (0, 64):
			f1.write("Core")
			f1.write("%s:\n\n" % (core+1))
			f2.write("Core")
			f2.write("%s:\n\n" % (core+1))
			f3.write("Core")
			f3.write("%s:\n\n" % (core+1))
			x = (core//8)*1120
			y= (core%8)*1120
			f1.write("  position       %s,    %s ;\n" % (x, y))
			f1.write("  dimension   1120, 1120 ;\n\n")
			f1.write("  power values ")
			f2.write("  position       %s,    %s ;\n" % (x, y))
			f2.write("  dimension   1120, 1120 ;\n\n")
			f2.write("  power values ")
			f3.write("  position       %s,    %s ;\n" % (x, y))
			f3.write("  dimension   1120, 1120 ;\n\n")
			f3.write("  power values ")
			for i in range (0, len(c_p_u)):
				#print c_i_u[i][1]
				if (float (c_i_u[i][1]) == 0.0):
					f1.write("%s, " % c_p_u[i][core])
					f2.write("0, ")
					f3.write("0, ")	
				else:
					f1.write("%s " % c_p_u[i][core])
					f2.write("0 ")
					f3.write("0 ")
					break
			f1.write(";\n\n")
			f2.write(";\n\n")
			f3.write(";\n\n")		
		f1.close()
		f2.close()
		f3.close()
		# End of creation of floor plans for 3D-ICE tool
		#--------------------------------------------------------------------------------------------
		#create a stack file for each benchmark which is also given as input to 3D-ICE tool
		current_bechmark_stk_path = file_path+aplication+'_'+chip_core+'_'+threads+'/stack_file_migration_3layer.stk'
		f4 = open(current_bechmark_stk_path,'w')
		f4.write("material SILICON :\n")
		f4.write("   thermal conductivity     1.30e-4 ;\n")
		f4.write("   volumetric heat capacity 1.628e-12 ;\n\n")
		f4.write("material SIO2 :\n")
		f4.write("   thermal conductivity     1.46e-6 ;\n")
		f4.write("   volumetric heat capacity 1.628e-12 ;\n\n")
		f4.write("material BEOL :\n")
		f4.write("   thermal conductivity     2.25e-6 ;\n")
		f4.write("   volumetric heat capacity 2.175e-12 ;\n\n")
		f4.write("material COPPER :\n")
		f4.write("   thermal conductivity     5.85e-4 ;\n")
		f4.write("   volumetric heat capacity 3.45e-12 ;\n\n")
		f4.write("connection to ambient:\n")
		f4.write("   heat transfer coefficient 1.0e-7;\n")
		f4.write("   ambient temperature 300;\n\n")
		f4.write("layer PCB :\n")
		f4.write("   height 10 ;\n")
		f4.write("   material BEOL ;\n\n")
		f4.write("die TOP_IC :\n")
		f4.write("   source  2 SILICON ;\n")
		f4.write("   layer  50 SILICON ;\n\n")
		f4.write("die ANALOG_IC :\n")
		f4.write("   layer  10 BEOL ;\n")
		f4.write("   source  2 SILICON ;\n") 
		f4.write("   layer  50 SILICON ;\n\n")
		f4.write("die PHTOTNIC_IC :\n")
		f4.write("   layer   5 BEOL;\n")
		f4.write("   source 0.1 SILICON ;\n")
		f4.write("   layer  0.2 SIO2 ;\n")
		f4.write("   layer  50 SILICON ;\n\n")
		f4.write("dimensions :\n")
		f4.write("   chip length 8960, width 8960 ;\n")
		f4.write("   cell length 560, width 560 ;\n\n")
		f4.write("stack:\n")
		#Load floor plans which are previously created using power traces
		f4.write('   die     TIER1     TOP_IC    floorplan "./Power_trace_migration_layout_Electrical.flp" ;\n')
		f4.write('   die     TIER2     ANALOG_IC floorplan "./Power_trace_migration_layout_Photonic1.flp" ;\n')
		f4.write('   die     TIER3     PHTOTNIC_IC floorplan "./Power_trace_migration_layout_Photonic1.flp" ;\n')
		f4.write('   die     TIER4     PHTOTNIC_IC floorplan "./Power_trace_migration_layout_Photonic2.flp" ;\n')
		f4.write("   layer   CONN_TO_PCB    PCB ;\n\n")
		f4.write("solver:\n")
		f4.write("   transient step 0.00001, slot 0.0001 ;\n")
		f4.write("   initial temperature 303.0 ;\n\n")
		#Specify location to store output temeparture trace results from the 3D-ICE tool
		current_benchmark_directory = file_path+aplication+'_'+chip_core+'_'+threads
		current_benchmark_E_temperature_path = file_path+aplication+'_'+chip_core+'_'+threads+'/Temperature_trace_migration_Electrical.csv'
		current_benchmark_P1_temperature_path = file_path+aplication+'_'+chip_core+'_'+threads+'/Temperature_trace_migration_Photonic1.csv'
		current_benchmark_P2_temperature_path = file_path+aplication+'_'+chip_core+'_'+threads+'/Temperature_trace_migration_Photonic2.csv'
		f4.write("output:\n")
		f4.write('   Tflp     (  TIER1,             "Temperature_trace_migration_Electrical.csv", average,    slot ) ;\n\n')
		f4.write('   Tflp     (  TIER3,             "Temperature_trace_migration_Photonic1.csv", average,    slot ) ;\n\n')
		f4.write('   Tflp     (  TIER4,             "Temperature_trace_migration_Photonic2.csv", average,    slot ) ;\n\n')
		f4.close()
		# End of creation of stack file for each benchmark
		#--------------------------------------------------------------------------------------------
		# Creating temporary power and IPC trace files
		c_i_u_mt = c_i_u
		c_p_u_mt = c_p_u
		# This files is created to monitor the process of thread migration
		output_file_path = 'Output_for_benchmark/output_file'+'_'+aplication+'_'+threads+'.txt'
		f_print = open(output_file_path, 'w') # File that monitors thread migraiton process
		Thermal_thershold = 343 # Thermal thershold to migrate threads is set to 343K 
		Thread_migration_count = 0 # Intialize number of thread migrations
		
		# Intialize arrays that captures critical parameters in each iteration
		t_max = [] # Paramater that monitors peak temperature
		t_max_p = [] # Paramater that monitors predicted peak temperature
		t_power = [] # Paramater that monitors trimming and tuning power dissipation
		f_results.write("")
		#--------------------------------------------------------------------------------------------
		# Creating temporary power and IPC trace files
		# Loop that iterates for each epoch and do migration of threads at the end of each epoch
		for e in range (Iterations):
			f_print.write("Current Iteration : %d \n" %(e))
			# Call 3D ICE to generate thermal trace for current epoc
			# Running 3D-ICE tool to generate temeperature traces
			call(['cp', current_benchmark_E_floor_plan_path ,'/home/vineel/csvfiles/PYML/PyML-0.7.13.2/Temperature_prediction/PDTM' ])
			call(['cp', current_benchmark_P1_floor_plan_path ,'/home/vineel/csvfiles/PYML/PyML-0.7.13.2/Temperature_prediction/PDTM' ])
			call(['cp', current_benchmark_P2_floor_plan_path ,'/home/vineel/csvfiles/PYML/PyML-0.7.13.2/Temperature_prediction/PDTM' ])
			call(['cp', current_bechmark_stk_path ,'/home/vineel/csvfiles/PYML/PyML-0.7.13.2/Temperature_prediction/PDTM' ])
			call(["/home/vineel/3d-ice/bin/3D-ICE-Emulator", "stack_file_migration_3layer.stk"])
			call(['cp', "Temperature_trace_migration_Electrical.csv" ,current_benchmark_directory ])
			call(['cp', "Temperature_trace_migration_Photonic1.csv" ,current_benchmark_directory ])
			call(['cp', "Temperature_trace_migration_Photonic2.csv" ,current_benchmark_directory ])
			# Process temerature trace to make it suitable  input for SVR to predict future temperature
			f_t = open('Temperature_trace_migration_Electrical.csv', 'rb')
			rows = list(csv.reader(f_t))   # Loading rows of temerature traces
			# Check and process last line which has information about current simulation status
			t = rows[len(rows)-1][0].split()
			t_f = [0 for x in range(len(t)-1)] # Array to store future temeperature
			t_a = [0 for x in range(len(t)-1)] # Array to store average neighbouring core temeperature
			i_a = [0 for x in range(len(t)-1)] # Array to store average IPC of core in the current epoc
			#--------------------------------------------------------------------------------------------
			# Loop that calculates average temperature of neghbouring cores 
			for n in range (0, 64):
					if (n%8 == 0):
						k1 = float("3.000e+02")
						k2 = float(t[n+2])
						if (n == 0):
							k3 = float("3.000e+02")
						else:
							k3 = float(t[n+1-8])
						if (n == 56):
							k4 = float("3.000e+02")
						else:
							k4 = float(t[n+1+8])
						k = (k1+k2+k3+k4)/4 # compute average temeprature feature
						t_a[n] = k          # store average surrounding core temperature in an array
						# agregate instrcution count
						current_ipc = 0
						for count in range (0, 10):
							current_ipc = current_ipc + float(c_i_u_mt[len(rows)-3-count][n])
						current_ipc_avg = current_ipc/10
						i_a [n] = current_ipc_avg
					elif (n%8 == 7):
					   k1 = float(t[n])
					   k2 = float("3.000e+02")
					   if (n == 7):
						  k3 = float("3.000e+02")
					   else:
						  k3 = float(t[n+1-8])
					   if (n == 63):
						  k4 = float("3.000e+02")
					   else:
						  k4 = float(t[n+1+8])
					   k = (k1+k2+k3+k4)/4 # compute average temeprature feature
					   t_a[n] = k          # store average surrounding core temperature in an array
					   # agregate instrcution count
					   current_ipc = 0
					   for count in range (0, 10):
						   current_ipc = current_ipc + float(c_i_u_mt[len(rows)-3-count][n])
					   current_ipc_avg = current_ipc/10
					   i_a [n] = current_ipc_avg
					elif (n>0 and n < 7 ):
					   k1 = float(t[n])
					   k2 = float(t[n+2])
					   k3 = float("3.000e+02")
					   k4 = float(t[n+1+8])
					   k = (k1+k2+k3+k4)/4 # compute average temeprature feature
					   t_a[n] = k          # store average surrounding core temperature in an array
					   # agregate instrcution count
					   current_ipc = 0
					   for count in range (0, 10):
						   current_ipc = current_ipc + float(c_i_u_mt[len(rows)-3-count][n])
					   current_ipc_avg = current_ipc/10
					   i_a [n] = current_ipc_avg
					elif (n>56 and n < 63 ):
					   k1 = float(t[n])
					   k2 = float(t[n+2])
					   k3 = float(t[n+1-8])
					   k4 = float("3.000e+02")
					   k = (k1+k2+k3+k4)/4 # compute average temeprature feature
					   t_a[n] = k          # store average surrounding core temperature in an array
					   # agregate instrcution count
					   current_ipc = 0
					   for count in range (0, 10):
						   current_ipc = current_ipc + float(c_i_u_mt[len(rows)-3-count][n])
					   current_ipc_avg = current_ipc/10
					   i_a [n] = current_ipc_avg
					else:
					   k1 = float(t[n])
					   k2 = float(t[n+2])
					   k3 = float(t[n+1-8])
					   k4 = float(t[n+1+8])
					   k = (k1+k2+k3+k4)/4 # compute average temeprature feature
					   t_a[n] = k          # store average surrounding core temperature in an array
					   # agregate instrcution count
					   current_ipc = 0
					   for count in range (0, 10):
						   current_ipc = current_ipc + float(c_i_u_mt[len(rows)-3-count][n])
					   current_ipc_avg = current_ipc/10
					   i_a [n] = current_ipc_avg
			# End of loop that calculates average temperature of neghbouring cores 
			#--------------------------------------------------------------------------------------------
			# Call linear regressor to predict future temeperature
			f_print.write("Calling Linear regressor to predict future temeperature \n")
			# Loop that iterates over all cores to generates future temperature
			for n in range (0, 64):
				# Linear regressor takes IPC, current core temeprature, and neghbouring cores temperatures are given as imputs
				t_f[n] = y_rbf.predict([t[n+1],t_a[n],i_a[n]])
				f_print.write("%s, %f, %f, %f \n" %(t[n+1],t_a[n],i_a[n],t_f[n]))
			# End of Loop that generates future temperature
			t_float = []
			# Loop that converts temepratures from string data type to float data type
			for f in range (len(t)-1):
				t_float.append(float(t[f+1]))
			# End of loop that converts temepratures from string data type to float data type
			#--------------------------------------------------------------------------------------------
			t_max.append(max(t_float)) # Computing on-chip peak temeparture
			t_max_p.append(max(t_f))   # Computing on-chip predicted future peak temeparture
			# Check for thread migration and Generate power map for each iteration
            # Compute average temeperature around each ring block
			t_rb = [0 for x in range(16)] # Array to store ring block temperature
			# Loop that computes ring blocks current temperature
			for i in range (0,16):
				temp = ((2*(i%4))+1)+(i//4)*16
				t1 = float(t[temp])
				t2 = float(t[temp+1])
				t3 = float(t[temp+8])
				t4 = float(t[temp+9])
				t_avg = (t1+t2+t3+t4)/4
				t_rb[i] = t_avg
 			# End of loop that computes ring blocks current temperature
 			#--------------------------------------------------------------------------------------------
 			#Compute trimming power in this epoc
 			tp_rb = [] # variable that store trimming power of current epoc
 			# Loop that iterate over ring blocks to compute trimming and tuning power 
 			for i in range (0,16):
				temp = abs(303 - t_rb[i])*0.04863
				tp_rb.append(temp)
 			# End of Loop that iterate over ring blocks to compute trimming and tuning power 
 			avg_tp = sum(tp_rb) # Total tuning power in this epoc for each ring of block
 			f_print.write("Average trimming power per epoc: %f \n" %(avg_tp))
 			t_power.append(avg_tp)
			#--------------------------------------------------------------------------------------------
 			#Code that find migration pairs in each Epoch
			mir_pair = [] # Array that stores thread migration pairs in each epoch
			# finding indexes of free cores
			cool_free_core = []
			# Loop that checks for free cores whose predicted temeprature is lesser than thermal thershold
			for n in range (0,64):
				if (i_a[n] == 0 and t_f[n] < Thermal_thershold):
					cool_free_core.append([n, t_f[n]])
			# End of loop that checks for free cores whose predicted temeprature is lesser than thermal thershold
			# Sort freecores as per their temeprature
			s_cool_free_cores = sorted(cool_free_core,key=lambda x: x[1])
			f_print.write("Trying to migrate threads...................\n")
			# Loop that finds cores whose temeprature exceeds thermal thershold and attempt to migrate threads
			for n in range (0,64):
				if (t_f[n] > Thermal_thershold and len(s_cool_free_cores)>0):
					f_print.write("Need for migration\n")
					# Check the availability of cores and migrate to future coolest core
					mir_pair.append([n, s_cool_free_cores[0][0]]) # Store migration pair 
					f_print.write("Migration pair %d %d \n" %(n, s_cool_free_cores[0][0]))
					s_cool_free_cores.pop(0)
					Thread_migration_count = Thread_migration_count + 1
			# End of loop that attempts to do thread migration in each epoch
			#--------------------------------------------------------------------------------------------
			# Loop that update traces based on the migration pairs 
			for m in range (len(mir_pair)):
				f_print.write("Migrating thread %d and doing trace reconfiguration\n" %(m))
				for trace in range (len(rows)-2, len(c_i_u)):
					temp = c_i_u_mt[trace][mir_pair[m][0]]
					c_i_u_mt[trace][mir_pair[m][0]] = c_i_u_mt[trace][mir_pair[m][1]]
					c_i_u_mt[trace][mir_pair[m][1]] = temp
					temp = c_p_u_mt[trace][mir_pair[m][0]]
					c_p_u_mt[trace][mir_pair[m][0]] = c_p_u_mt[trace][mir_pair[m][1]]
					c_p_u_mt[trace][mir_pair[m][1]] = temp
			# End of loop that update traces based on the migration pairs 
			#--------------------------------------------------------------------------------------------
			# Generate updated floor plan maps using updated traces for 3D-ICE tool which will be used for next iteration
			f1 = open(current_benchmark_E_floor_plan_path,'w')
			f2 = open(current_benchmark_P1_floor_plan_path,'w')
			f3 = open(current_benchmark_P2_floor_plan_path,'w')
			last_line = len(rows)-2 + current_interval # Computing lastline
			f_print.write("Last Line: %d, cureent rows: %d, current_interval: %d \n" %(last_line, len(rows)-2, current_interval))
			for core in range (0, 64):
				f1.write("Core")
				f1.write("%s:\n\n" % (core+1))
				f2.write("Core")
				f2.write("%s:\n\n" % (core+1))
				f3.write("Core")
				f3.write("%s:\n\n" % (core+1))
				x = (core//8)*1120
				y= (core%8)*1120
				f1.write("  position       %s,    %s ;\n" % (x, y))
				f1.write("  dimension   1120, 1120 ;\n\n")
				f1.write("  power values ")
				f2.write("  position       %s,    %s ;\n" % (x, y))
				f2.write("  dimension   1120, 1120 ;\n\n")
				f2.write("  power values ")
				f3.write("  position       %s,    %s ;\n" % (x, y))
				f3.write("  dimension   1120, 1120 ;\n\n")
				f3.write("  power values ")
				for i in range (0, last_line):
					if (i != (last_line-1)):
						f1.write("%s, " % c_p_u_mt[i][core])
						f2.write("0, ")
						f3.write("0, ")	
					else:
						f1.write("%s " % c_p_u_mt[i][core])
						f2.write("0 ")
						f3.write("0 ")
				f1.write(";\n\n")
				f2.write(";\n\n")
				f3.write(";\n\n")		
			f1.close()
			f2.close()
			f3.close()
		# End of creation of floor plan files for the next iteration
		#--------------------------------------------------------------------------------------------
		f_print.close() # Close file that monitors thread migraiton process
		# Result genertaion for the PDTM thread migration mechanism
		f_results.write("Number of thread migrations: %d\n" %(Thread_migration_count))
		f_results.write("Execution time (In ms): %f\n" %(Iterations + (Thread_migration_count * 0.01)))
		f_results.write("Migration overhead (In ms): %f\n" %(Thread_migration_count * 0.01))
		f_results.write("Trimming Power (In mW): %f\n" %(np.mean(t_power)))
		C_TP = 256 * 4 * 64 *(np.mean(t_power))
		f_results.write("Trimming Power for Corona (In mW): %f\n" %(C_TP))
		f_results.write("Actual maximum temeperatures on chip: \n")
		f_results.write("[")
		for i in range (len(t_max)):
			f_results.write("%s " %(t_max[i]))
		f_results.write("]\n")
		f_results.write("Predicted maximum temeperatures on chip: \n")
		f_results.write("[")
		for i in range (len(t_max_p)):
			f_results.write("%s " %(t_max_p[i]))
		f_results.write("]\n")

				
		   
					
					
