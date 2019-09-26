from __future__ import division
from pyomo.environ import *
#from pyomo.core.expr  import current as EXPR
#import numpy as np
import math
import csv
import random
model = AbstractModel()

########
##SETS##
########

#Define the sets

print("Declaring sets...")

#Supply technology sets
model.Generator = Set(ordered=True, initialize = ['Coal','HydroReg','Solar','Wind','Bio']) #g
model.Technology = Set(ordered=True, initialize = ['Fossil','Hydro','RES']) #t
model.Storage =  Set(initialize = ['Liion','HydroPump']) #b

#Temporal sets
model.Period = Set(initialize = [1,2,3,4,5,6,7,8,9], ordered=True) #i
model.Operationalhour = Set(initialize = [1,2,3,4,5], ordered=True) #h
model.Season = Set(initialize = ['winter','summer'], ordered=True) #s

#Spatial sets
model.Node = Set(ordered=True, initialize = ['Germany','Denmark']) #n
model.DirectionalLink = Set(dimen=2, within=model.Node*model.Node, ordered=True, initialize = [('Germany','Denmark'),('Denmark','Germany')]) #a

#Stochastic sets
model.Scenario = Set(initialize = ['sce1','sce2','sce3','sce4','sce5'], ordered=True) #w

#Subsets
model.GeneratorsOfTechnology=Set(dimen=2, initialize = [('Fossil','Coal'),('Hydro','HydroReg'),('RES','Solar'),('RES','Wind'),('RES','Bio')]) #(t,g) for all t in T, g in G_t
model.GeneratorsOfNode = Set(dimen=2, initialize = [('Germany','Coal'),('Germany','HydroReg'),('Germany','Solar'),('Germany','Wind'),('Denmark','Wind'),('Denmark','Bio')]) #,('Denmark','Coal'),('Denmark','Solar') #(n,g) for all n in N, g in G_n
model.ThermalGenerators = Set(within=model.Generator, initialize = ['Coal','Bio']) #g_
model.RegHydroGenerator = Set(within=model.Generator, initialize = ['HydroReg']) #g_reghyd
model.HydroGenerator = Set(within=model.Generator, initialize = ['HydroReg']) #g_hyd
model.StoragesOfNode = Set(dimen=2, initialize = [('Germany','Liion'),('Germany','HydroPump')]) #(n,b) for all n in N, b in B_n
model.DependentStorage = Set(within=model.Storage, initialize = ['Liion']) #b_dagger
model.HoursOfSeason = Set(dimen=2, initialize = [('winter',1),('winter',2),('winter',3),('winter',4),('winter',5),('summer',1),('summer',2),('summer',3),('summer',4),('summer',5)], ordered=True) #(s,h) for all s in S, h in H_s
#model.FirstHoursOfSeason = Set(within=model.Operationalhour, initialize=[1])
#model.FirstHoursOfPeakSeason = Set(within=model.Operationalhour, initialize=[6])

print("Constructing sub sets...")

#Build arc subsets

def NodesIn_init(model, node):
    retval = []
    for (i,j) in model.DirectionalLink:
        if j == node:
            retval.append(i)
    return retval
model.NodesIn = Set(model.Node, initialize=NodesIn_init)

def NodesOut_init(model, node):
    retval = []
    for (i,j) in model.DirectionalLink:
        if i == node:
            retval.append(j)
    return retval
model.NodesOut = Set(model.Node, initialize=NodesOut_init)

def BidirectionalArc_init(model):
    retval = []
    for (i,j) in model.DirectionalLink:
        if i != j and (not (j,i) in retval):
            retval.append((i,j))
    return retval
model.BidirectionalArc = Set(dimen=2, initialize=BidirectionalArc_init, ordered=True) #l

#instance = model.create_instance()
#instance.NodesOut.pprint()
#instance.BidirectionalArc.pprint()
#import pdb; pdb.set_trace()

##############
##PARAMETERS##
##############

#Define the parameters

print("Declaring parameters...")

#Scaling

model.discountrate = Param(initialize=0.05)
model.LeapYearsInvestment = Param(initialize=5)
model.operationalDiscountrate = Param(initialize=0.05, mutable=True)
model.sceProbab = Param(model.Scenario, initialize=0.2)
model.seasScale = Param(model.Season, initialize=876)
model.lengthSeason = Param(model.Season, initialize=5)
#model.lengthPeakSeason = Param(initialize=5)

#Cost

model.genInvCost = Param(model.Generator, model.Period, initialize=2183752.0)
model.transmissionInvCost = Param(model.BidirectionalArc, model.Period, initialize=353750.0)
model.storPWInvCost = Param(model.Storage, model.Period, initialize=100000.0)
model.storENInvCost = Param(model.Storage, model.Period, initialize=100000.0)
model.genMargCost = Param(model.Generator, model.Period, initialize=25.0)
model.genCO2factor = Param(model.Generator, model.Period, initialize=0.8)
model.nodeLostLoadCost = Param(model.Node, model.Period, default=22000.0)
model.CO2cap = Param(model.Period, default=210000000.0)

#Node dependent technology limitations

model.genInitCap = Param(model.GeneratorsOfNode, model.Period, default=100.0, mutable=True)
model.transmissionInitCap = Param(model.BidirectionalArc, model.Period, default=100.0)
model.storPWInitCap = Param(model.StoragesOfNode, model.Period, default=100.0)
model.storENInitCap = Param(model.StoragesOfNode, model.Period, default=100.0)
model.genMaxBuiltCap = Param(model.Node, model.Technology, model.Period, default=200000.0, mutable=True)
model.transmissionMaxBuiltCap = Param(model.BidirectionalArc, model.Period, default=20000.0, mutable=True)
model.storPWMaxBuiltCap = Param(model.StoragesOfNode, model.Period, default=50000.0, mutable=True)
model.storENMaxBuiltCap = Param(model.StoragesOfNode, model.Period, default=50000.0, mutable=True)
model.genMaxInstalledCapRaw = Param(model.Node, model.Technology, default=100000.0, mutable=True)
model.genMaxInstalledCap = Param(model.Node, model.Technology, model.Period, default=0.0, mutable=True)
model.transmissionMaxInstalledCap = Param(model.BidirectionalArc, model.Period, default=1500.0, mutable=True)
model.storPWMaxInstalledCap = Param(model.StoragesOfNode, model.Period, default=0.0, mutable=True)
model.storPWMaxInstalledCapRaw = Param(model.StoragesOfNode, default=100000.0, mutable=True)
model.storENMaxInstalledCap = Param(model.StoragesOfNode, model.Period, default=0.0, mutable=True)
model.storENMaxInstalledCapRaw = Param(model.StoragesOfNode, default=100000.0, mutable=True)

#Type dependent technology limitations

model.genLifetime = Param(model.Generator, default=10.0)
model.transmissionLifetime = Param(model.BidirectionalArc, default=20.0)
model.storageLifetime = Param(model.Storage, default=10.0)
model.lineEfficiency = Param(model.DirectionalLink, default=0.97)
model.storageChargeEff = Param(model.Storage, default=0.9)
model.storageDischargeEff = Param(model.Storage, default=0.9)
model.genRampUpCap = Param(model.ThermalGenerators, default=0.1)
model.storageDiscToCharRatio = Param(model.Storage, default=1.0)
model.storagePowToEnergy = Param(model.DependentStorage, default=1.0)

#Stochastic input

model.sloadRaw = Param(model.Node, model.HoursOfSeason, model.Scenario, default=15000.0)
model.sloadAdjustment = Param(model.Node, model.Period, default=0.0, mutable=True)
model.sload = Param(model.Node, model.HoursOfSeason, model.Period, model.Scenario, default=0.0, mutable=True)
model.genCapAvailTypeRaw = Param(model.Generator, default=0.8, mutable=True) 
model.genCapAvailStochRaw = Param(model.GeneratorsOfNode, model.HoursOfSeason, model.Scenario, default=0.8, mutable=True)
model.genCapAvail = Param(model.GeneratorsOfNode, model.HoursOfSeason, model.Period, model.Scenario, default=0.0, mutable=True)
model.maxRegHydroGenRaw = Param(model.Node, model.HoursOfSeason, model.Scenario, default=1000.0, mutable=True)
model.maxRegHydroGen = Param(model.Node, model.Season, model.Period, model.Scenario, default=0.0, mutable=True)
model.maxHydroNode = Param(model.Node, default=100000.0, mutable=True)
model.storOperationalInit = Param(model.Storage, default=0.5, mutable=True) #Percentage of installed energy capacity 

print("Constructing parameter values...")

#Build operational discount rate

def prepOperationalDiscountrate_rule(model):
    model.operationalDiscountrate = sum((1+model.discountrate)**(-j) for j in list(range(0,value(model.LeapYearsInvestment))))

model.build_operationalDiscountrate = BuildAction(rule=prepOperationalDiscountrate_rule)    

#Build resource limit (installed limit) for all periods. Avoid infeasibility if installed limit lower than initially installed cap. 

def prepGenMaxInstalledCap_rule(model):
    for t in model.Technology:
        for n in model.Node:
            for i in model.Period:
                if value(model.genMaxInstalledCapRaw[n,t] <= sum(model.genInitCap[n,g,i] for g in model.Generator if (n,g) in model.GeneratorsOfNode and (t,g) in model.GeneratorsOfTechnology)):
                    model.genMaxInstalledCap[n,t,i]=sum(model.genInitCap[n,g,i] for g in model.Generator if (n,g) in model.GeneratorsOfNode and (t,g) in model.GeneratorsOfTechnology)
                else:
                    model.genMaxInstalledCap[n,t,i]=model.genMaxInstalledCapRaw[n,t]
                    
model.build_genMaxInstalledCap = BuildAction(rule=prepGenMaxInstalledCap_rule)

#Build installed limit (resource limit) for storEN

def storENMaxInstalledCap_rule(model):
    for (n,b) in model.StoragesOfNode:
        for i in model.Period:
            model.storENMaxInstalledCap[n,b,i]=model.storENMaxInstalledCapRaw[n,b]

model.build_storENMaxInstalledCap = BuildAction(rule=storENMaxInstalledCap_rule)

#Build installed limit (resource limit) for storPW

def storPWMaxInstalledCap_rule(model):
    for (n,b) in model.StoragesOfNode:
        for i in model.Period:
            model.storPWMaxInstalledCap[n,b,i]=model.storPWMaxInstalledCapRaw[n,b]

model.build_storPWMaxInstalledCap = BuildAction(rule=storPWMaxInstalledCap_rule)

#Build hydrolimits for all periods

def prepRegHydro_rule(model):
    for n in model.Node:
        for s in model.Season:
            for i in model.Period:
                for sce in model.Scenario:
                    model.maxRegHydroGen[n,s,i,sce]=sum(model.maxRegHydroGenRaw[n,s,h,sce] for h in model.Operationalhour if (s,h) in model.HoursOfSeason)

model.build_maxRegHydroGen = BuildAction(rule=prepRegHydro_rule)

#Build generator availability for all periods

def prepGenCapAvail_rule(model):
    for (n,g) in model.GeneratorsOfNode:
        for i in model.Period:
            for (s,h) in model.HoursOfSeason:
                for w in model.Scenario:
                    if model.genCapAvailTypeRaw[g] == 0:
                        model.genCapAvail[n,g,s,h,i,w]=model.genCapAvailStochRaw[n,g,s,h,w]
                    else:
                        model.genCapAvail[n,g,s,h,i,w]=model.genCapAvailTypeRaw[g]                        

model.build_genCapAvail = BuildAction(rule=prepGenCapAvail_rule)

#Build load profiles for all periods

def prepSload_rule(model):
    for n in model.Node:
        for (s,h) in model.HoursOfSeason:
            for sce in model.Scenario:
                for i in model.Period:
                    model.sload[n,s,h,i,sce]=model.sloadRaw[n,s,h,sce]+random.randint(-4800,5000)

model.build_sload = BuildAction(rule=prepSload_rule)

#instance = model.create_instance()
#instance.sload.pprint()
#import pdb; pdb.set_trace()

print("Sets and parameters declared and read...")

#############
##VARIABLES##
#############

print("Declaring variables...")

model.genInvCap = Var(model.GeneratorsOfNode, model.Period, domain=NonNegativeReals)
model.transmisionInvCap = Var(model.BidirectionalArc, model.Period, domain=NonNegativeReals)
model.storPWInvCap = Var(model.StoragesOfNode, model.Period, domain=NonNegativeReals)
model.storENInvCap = Var(model.StoragesOfNode, model.Period, domain=NonNegativeReals)
model.genOperational = Var(model.GeneratorsOfNode, model.HoursOfSeason, model.Period, model.Scenario, domain=NonNegativeReals)
model.storOperational = Var(model.StoragesOfNode, model.HoursOfSeason, model.Period, model.Scenario, domain=NonNegativeReals)
model.transmisionOperational = Var(model.DirectionalLink, model.HoursOfSeason, model.Period, model.Scenario, domain=NonNegativeReals) #flow
model.storCharge = Var(model.StoragesOfNode, model.HoursOfSeason, model.Period, model.Scenario, domain=NonNegativeReals)
model.storDischarge = Var(model.StoragesOfNode, model.HoursOfSeason, model.Period, model.Scenario, domain=NonNegativeReals)
model.loadShed = Var(model.Node, model.HoursOfSeason, model.Period, model.Scenario, domain=NonNegativeReals)
model.genInstalledCap = Var(model.GeneratorsOfNode, model.Period, domain=NonNegativeReals)
model.transmisionInstalledCap = Var(model.BidirectionalArc, model.Period, domain=NonNegativeReals)
model.storPWInstalledCap = Var(model.StoragesOfNode, model.Period, domain=NonNegativeReals)
model.storENInstalledCap = Var(model.StoragesOfNode, model.Period, domain=NonNegativeReals)

###############
##EXPRESSIONS##
###############

def multiplier_rule(model,period):
    coeff=1
    if period>1:
        coeff=pow(1.0+model.discountrate,(-5*(int(period)-1)))
    return coeff
model.discount_multiplier=Expression(model.Period, rule=multiplier_rule)

def shed_component_rule(model,i):
    return sum(model.operationalDiscountrate*model.seasScale[s]*model.sceProbab[w]*model.nodeLostLoadCost[n,i]*model.loadShed[n,s,h,i,w] for n in model.Node for w in model.Scenario for (s,h) in model.HoursOfSeason)
model.shedcomponent=Expression(model.Period,rule=shed_component_rule)

def operational_cost_rule(model,i):
    return sum(model.operationalDiscountrate*model.seasScale[s]*model.sceProbab[w]*model.genMargCost[g,i]*model.genOperational[n,g,s,h,i,w] for (n,g) in model.GeneratorsOfNode for (s,h) in model.HoursOfSeason for w in model.Scenario)
model.operationalcost=Expression(model.Period,rule=operational_cost_rule)

#############
##OBJECTIVE##
#############

def Obj_rule(model):
    return sum(model.discount_multiplier[i]*(sum(model.genInvCost[g,i]* model.genInvCap[n,g,i] for (n,g) in model.GeneratorsOfNode ) + \
        sum(model.transmissionInvCost[n1,n2,i]*model.transmisionInvCap[n1,n2,i] for (n1,n2) in model.BidirectionalArc ) + \
        sum((model.storPWInvCost[b,i]*model.storPWInvCap[n,b,i]+model.storENInvCost[b,i]*model.storENInvCap[n,b,i]) for (n,b) in model.StoragesOfNode ) + \
        model.shedcomponent[i] + model.operationalcost[i]) for i in model.Period)
model.Obj = Objective(rule=Obj_rule, sense=minimize)

###############
##CONSTRAINTS##
###############

def FlowBalance_rule(model, n, s, h, i, w):
    return sum(model.genOperational[n,g,s,h,i,w] for g in model.Generator if (n,g) in model.GeneratorsOfNode) \
    + sum((model.storageDischargeEff[b]*model.storDischarge[n,b,s,h,i,w]-model.storCharge[n,b,s,h,i,w]) for b in model.Storage if (n,b) in model.StoragesOfNode) \
    + sum((model.lineEfficiency[inflow,n]*model.transmisionOperational[inflow,n,s,h,i,w]) for inflow in model.NodesIn[n] ) \
    - sum((model.transmisionOperational[n,outflow,s,h,i,w]) for outflow in model.NodesOut[n] ) \
    - model.sload[n,s,h,i,w] + model.loadShed[n,s,h,i,w] \
    == 0
model.FlowBalance = Constraint(model.Node, model.HoursOfSeason, model.Period, model.Scenario, rule=FlowBalance_rule)

#################################################################

def genMaxProd_rule(model, n, g, s, h, i, w):
        return model.genOperational[n,g,s,h,i,w] - model.genCapAvail[n,g,s,h,i,w]*model.genInstalledCap[n,g,i] <= 0
model.maxGenProduction = Constraint(model.GeneratorsOfNode, model.HoursOfSeason, model.Period, model.Scenario, rule=genMaxProd_rule)

#################################################################

def ramping_rule(model, n, g, s, h, i, w):
    if h==1:
        return Constraint.Skip
    else:
        if g in model.ThermalGenerators:
            return model.genOperational[n,g,s,h,i,w]-model.genOperational[n,g,s,(h-1),i,w] - model.genRampUpCap[g]*model.genInstalledCap[n,g,i] <= 0   #
        else:
            return Constraint.Skip
model.ramping = Constraint(model.GeneratorsOfNode, model.HoursOfSeason, model.Period, model.Scenario, rule=ramping_rule)

#################################################################

def storage_energy_balance_rule(model, n, b, s, h, i, w):
    if h==1:
        return model.storOperationalInit[b]*model.storENInstalledCap[n,b,i] + model.storageChargeEff[b]*model.storCharge[n,b,s,h,i,w]-model.storDischarge[n,b,s,h,i,w]-model.storOperational[n,b,s,h,i,w] == 0   #
    else:
        return model.storOperational[n,b,s,(h-1),i,w] + model.storageChargeEff[b]*model.storCharge[n,b,s,h,i,w]-model.storDischarge[n,b,s,h,i,w]-model.storOperational[n,b,s,h,i,w] == 0   #
model.storage_energy_balance = Constraint(model.StoragesOfNode, model.HoursOfSeason, model.Period, model.Scenario, rule=storage_energy_balance_rule)

#################################################################

def storage_seasonal_net_zero_balance_rule(model, n, b, s, h, i, w):
    if h==1:
        return model.storOperational[n,b,s,h+value(model.lengthSeason[s])-1,i,w] - model.storOperationalInit[b]*model.storENInstalledCap[n,b,i] == 0  #
    else:
        return Constraint.Skip
model.storage_seasonal_net_zero_balance = Constraint(model.StoragesOfNode, model.HoursOfSeason, model.Period, model.Scenario, rule=storage_seasonal_net_zero_balance_rule)

#################################################################

def storage_operational_cap_rule(model, n, b, s, h, i, w):
    return model.storOperational[n,b,s,h,i,w] - model.storENInstalledCap[n,b,i]  <= 0   #
model.storage_operational_cap = Constraint(model.StoragesOfNode, model.HoursOfSeason, model.Period, model.Scenario, rule=storage_operational_cap_rule)

#################################################################

def storage_power_discharg_cap_rule(model, n, b, s, h, i, w):
    return model.storDischarge[n,b,s,h,i,w] - model.storageDiscToCharRatio[b]*model.storPWInstalledCap[n,b,i] <= 0   #
model.storage_power_discharg_cap = Constraint(model.StoragesOfNode, model.HoursOfSeason, model.Period, model.Scenario, rule=storage_power_discharg_cap_rule)

#################################################################

def storage_power_charg_cap_rule(model, n, b, s, h, i, w):
    return model.storCharge[n,b,s,h,i,w] - model.storPWInstalledCap[n,b,i] <= 0   #
model.storage_power_charg_cap = Constraint(model.StoragesOfNode, model.HoursOfSeason, model.Period, model.Scenario, rule=storage_power_charg_cap_rule)

#################################################################

def hydro_gen_limit_rule(model, n, g, s, i, w):
    if g in model.RegHydroGenerator:
        return sum(model.genOperational[n,g,s,h,i,w] for h in model.Operationalhour if (s,h) in model.HoursOfSeason) - model.maxRegHydroGen[n,s,i,w] <= 0
    else:
        return Constraint.Skip  #
model.hydro_gen_limit = Constraint(model.GeneratorsOfNode, model.Season, model.Period, model.Scenario, rule=hydro_gen_limit_rule)

#################################################################

def hydro_node_limit_rule(model, n, i):
    return sum(model.genOperational[n,g,s,h,i,w]*model.seasScale[s]*model.sceProbab[w] for g in model.HydroGenerator if (n,g) in model.GeneratorsOfNode for (s,h) in model.HoursOfSeason for w in model.Scenario) - model.maxHydroNode[n] <= 0   #
model.hydro_node_limit = Constraint(model.Node, model.Period, rule=hydro_node_limit_rule)

#################################################################

def transmission_cap_rule(model, n1, n2, s, h, i, w):
    if (n1,n2) in model.DirectionalLink and (n1,n2) in model.BidirectionalArc:
        return (model.transmisionOperational[(n1,n2),s,h,i,w]  - model.transmisionInstalledCap[(n1,n2),i] <= 0)
    elif (n1,n2) in model.DirectionalLink and (n2,n1) in model.BidirectionalArc:
        return (model.transmisionOperational[(n1,n2),s,h,i,w]  - model.transmisionInstalledCap[(n2,n1),i] <= 0)
    else:
        return Constraint.Skip
model.transmission_cap = Constraint(model.DirectionalLink, model.HoursOfSeason, model.Period, model.Scenario, rule=transmission_cap_rule)

#################################################################

def emission_cap_rule(model, i, w):
    return sum(model.seasScale[s]*model.genCO2factor[g,i]*model.genOperational[n,g,s,h,i,w] for (n,g) in model.GeneratorsOfNode for (s,h) in model.HoursOfSeason) - model.CO2cap[i] <= 0   #
model.emission_cap = Constraint(model.Period, model.Scenario, rule=emission_cap_rule)

#################################################################

def lifetime_rule_gen(model, n, g, i):
    startPeriod=1
    if value(1+i-(model.genLifetime[g]/model.LeapYearsInvestment))>startPeriod:
        startPeriod=math.floor(1+i-model.genLifetime[g]/model.LeapYearsInvestment)
    return sum(model.genInvCap[n,g,j]  for j in model.Period if j>=startPeriod and j<=i )- model.genInstalledCap[n,g,i] + model.genInitCap[n,g,i]== 0   #
model.installedCapDefinitionGen = Constraint(model.GeneratorsOfNode, model.Period, rule=lifetime_rule_gen)

#################################################################

def lifetime_rule_storEN(model, n, b, i):
    startPeriod=1
    if math.floor(1+i-model.storageLifetime[b]*(1/model.LeapYearsInvestment))>startPeriod:
        startPeriod=math.floor(1+i-model.storageLifetime[b]/model.LeapYearsInvestment)
    return sum(model.storENInvCap[n,b,j]  for j in model.Period if j>=startPeriod and j<=i )- model.storENInstalledCap[n,b,i] + model.storENInitCap[n,b,i]== 0   #
model.installedCapDefinitionStorEN = Constraint(model.StoragesOfNode, model.Period, rule=lifetime_rule_storEN)

#################################################################

def lifetime_rule_storPOW(model, n, b, i):
    startPeriod=1
    if math.floor(1+i-model.storageLifetime[b]*(1/model.LeapYearsInvestment))>startPeriod:
        startPeriod=math.floor(1+i-model.storageLifetime[b]/model.LeapYearsInvestment)
    return sum(model.storPWInvCap[n,b,j]  for j in model.Period if j>=startPeriod and j<=i )- model.storPWInstalledCap[n,b,i] + model.storPWInitCap[n,b,i]== 0   #
model.installedCapDefinitionStorPOW = Constraint(model.StoragesOfNode, model.Period, rule=lifetime_rule_storPOW)

#################################################################

def lifetime_rule_trans(model, n1, n2, i):
    startPeriod=1
    if math.floor(1+i-model.transmissionLifetime[n1,n2]*(1/model.LeapYearsInvestment))>startPeriod:
        startPeriod=math.floor(1+i-model.transmissionLifetime[n1,n2]/model.LeapYearsInvestment)
    return sum(model.transmisionInvCap[n1,n2,j]  for j in model.Period if j>=startPeriod and j<=i )- model.transmisionInstalledCap[n1,n2,i] + model.transmissionInitCap[n1,n2,i] == 0   #
model.installedCapDefinitionTrans = Constraint(model.BidirectionalArc, model.Period, rule=lifetime_rule_trans)

#################################################################

def investment_gen_cap_rule(model, t, n, i):
    return sum(model.genInvCap[n,g,i] for g in model.Generator if (n,g) in model.GeneratorsOfNode and (t,g) in model.GeneratorsOfTechnology) - model.genMaxBuiltCap[n,t,i] <= 0
model.investment_gen_cap = Constraint(model.Technology, model.Node, model.Period, rule=investment_gen_cap_rule)

#################################################################

def investment_trans_cap_rule(model, n1, n2, i):
    return model.transmisionInvCap[n1,n2,i] - model.transmissionMaxBuiltCap[n1,n2,i] <= 0
model.investment_trans_cap = Constraint(model.BidirectionalArc, model.Period, rule=investment_trans_cap_rule)

#################################################################

def investment_storage_power_cap_rule(model, n, b, i):
    return model.storPWInvCap[n,b,i] - model.storPWMaxBuiltCap[n,b,i] <= 0
model.investment_storage_power_cap = Constraint(model.StoragesOfNode, model.Period, rule=investment_storage_power_cap_rule)

#################################################################

def investment_storage_energy_cap_rule(model, n, b, i):
    return model.storENInvCap[n,b,i] - model.storENMaxBuiltCap[n,b,i] <= 0
model.investment_storage_energy_cap = Constraint(model.StoragesOfNode, model.Period, rule=investment_storage_energy_cap_rule)

################################################################

def installed_gen_cap_rule(model, t, n, i):
    return sum(model.genInstalledCap[n,g,i] for g in model.Generator if (n,g) in model.GeneratorsOfNode and (t,g) in model.GeneratorsOfTechnology) - model.genMaxInstalledCap[n,t,i] <= 0
model.installed_gen_cap = Constraint(model.Technology, model.Node, model.Period, rule=installed_gen_cap_rule)

#################################################################

def installed_trans_cap_rule(model, n1, n2, i):
    return model.transmisionInstalledCap[n1,n2,i] - model.transmissionMaxInstalledCap[n1,n2,i] <= 0
model.installed_trans_cap = Constraint(model.BidirectionalArc, model.Period, rule=installed_trans_cap_rule)

#################################################################

def installed_storage_power_cap_rule(model, n, b, i):
    return model.storPWInstalledCap[n,b,i] - model.storPWMaxInstalledCap[n,b,i] <= 0
model.installed_storage_power_cap = Constraint(model.StoragesOfNode, model.Period, rule=installed_storage_power_cap_rule)

#################################################################

def installed_storage_energy_cap_rule(model, n, b, i):
    return model.storENInstalledCap[n,b,i] - model.storENMaxInstalledCap[n,b,i] <= 0
model.installed_storage_energy_cap = Constraint(model.StoragesOfNode, model.Period, rule=installed_storage_energy_cap_rule)

#################################################################

def power_energy_relate_rule(model, n, b, i):
    if b in model.DependentStorage:
        return model.storPWInstalledCap[n,b,i] - model.storagePowToEnergy[b]*model.storENInstalledCap[n,b,i] <= 0   #
    else:
        return Constraint.Skip
model.power_energy_relate = Constraint(model.StoragesOfNode, model.Period, rule=power_energy_relate_rule)

#################################################################

#######
##RUN##
#######

print("Objective and constraints read...")

print("Building instance...")

instance = model.create_instance()
instance.dual = Suffix(direction=Suffix.IMPORT) #Make sure the dual value is collected into solver results (if solver supplies dual information)

#instance.genCapAvail.pprint()
#import pdb; pdb.set_trace()

print("----------------------Problem Statistics---------------------")
print("Nodes: "+ str(len(instance.Node)))
print("Lines: "+str(len(instance.BidirectionalArc)))
print("")
print("GeneratorTypes: "+str(len(instance.Generator)))
print("TotalGenerators: "+str(len(instance.GeneratorsOfNode)))
print("StorageTypes: "+str(len(instance.Storage)))
print("TotalStorages: "+str(len(instance.StoragesOfNode)))
print("")
print("InvestmentYears: "+str(len(instance.Period)))
print("Scenarios: "+str(len(instance.Scenario)))
print("TotalOperationalHoursPerScenario: "+str(len(instance.Operationalhour)))
print("TotalOperationalHoursPerInvYear: "+str(len(instance.Operationalhour)*len(instance.Scenario)))
print("Seasons: "+str(len(instance.Season)))
for s in instance.Season:
    print("LengthOfSeason "+str(s)+": "+str(value(instance.lengthSeason[s])))
print("--------------------------------------------------------------")

print("Solving...")

opt = SolverFactory('gurobi', solver_io='python', Verbose=True)
opt.options["Crossover"]=0
opt.options["Method"]=2
results = opt.solve(instance, tee=True) #keepfiles=True
#instance.display('outputs_gurobi.txt')
instance.emission_cap.pprint()
import pdb; pdb.set_trace()
###########
##RESULTS##
###########


print("Writing results to .csv...")

f = open('results_output_gen.csv', 'w', newline='')
writer = csv.writer(f)
writer.writerow(["Node,GeneratorType,Period,genInvCap_MW,genInstalledCap_MW,genExpectedCapacityFactor,DiscountedInvestmentCost_EuroPerMW,genExpectedAnnualProduction_GWh"])
for (n,g) in instance.GeneratorsOfNode:
    for i in instance.Period:
        my_string=str(n)+","+str(g)+","+str(value(2010+(i-1)*5))+","+str(value(instance.genInvCap[n,g,i]))+","+str(value(instance.genInstalledCap[n,g,i]))+","+ \
        str(value(sum(instance.sceProbab[w]*instance.seasScale[s]*instance.genOperational[n,g,s,h,i,w] for (s,h) in instance.HoursOfSeason for w in instance.Scenario)/(instance.genInstalledCap[n,g,i]*8760) if instance.genInstalledCap[n,g,i] != 0 else 0))+","+ \
        str(value(instance.discount_multiplier[i]*instance.genInvCap[n,g,i]*instance.genInvCost[g,i]))+","+ \
        str(value(sum(instance.seasScale[s]*instance.sceProbab[w]*instance.genOperational[n,g,s,h,i,w]/1000 for (s,h) in instance.HoursOfSeason for w in instance.Scenario)))  
        writer.writerow([my_string])
f.close()

f = open('results_output_stor.csv', 'w', newline='')
writer = csv.writer(f)
writer.writerow(["Node,StorageType,Period,storPWInvCap_MW,storPWInstalledCap_MW,storENInvCap_MWh,storENInstalledCap_MWh,DiscountedInvestmentCostPWEN_EuroPerMWMWh,ExpectedAnnualDischargeVolume_GWh,ExpectedAnnualLossesChargeDischarge_GWh"])
for (n,b) in instance.StoragesOfNode:
    for i in instance.Period:
        my_string=str(n)+","+str(b)+","+str(value(2010+(i-1)*5))+","+str(value(instance.storPWInvCap[n,b,i]))+","+str(value(instance.storPWInstalledCap[n,b,i]))+","+ \
        str(value(instance.storENInvCap[n,b,i]))+","+str(value(instance.storENInstalledCap[n,b,i]))+","+ \
        str(value(instance.discount_multiplier[i]*(instance.storPWInvCap[n,b,i]*instance.storPWInvCost[b,i] + instance.storENInvCap[n,b,i]*instance.storENInvCost[b,i])))+","+ \
        str(value(sum(instance.sceProbab[w]*instance.seasScale[s]*(instance.storDischarge[n,b,s,h,i,w] - instance.storCharge[n,b,s,h,i,w])/1000 for (s,h) in instance.HoursOfSeason for w in instance.Scenario)))+","+ \
        str(value(sum(instance.sceProbab[w]*instance.seasScale[s]*((1 - instance.storageDischargeEff[b])*instance.storDischarge[n,b,s,h,i,w] + (1 - instance.storageChargeEff[b])*instance.storCharge[n,b,s,h,i,w])/1000 for (s,h) in instance.HoursOfSeason for w in instance.Scenario)))
        writer.writerow([my_string])
f.close()

f = open('results_output_transmision.csv', 'w', newline='')
writer = csv.writer(f)
writer.writerow(["BetweenNode,AndNode,Period,transmisionInvCap_MW,transmisionInstalledCap_MW,DiscountedInvestmentCost_EuroPerMW,transmisionExpectedAnnualVolume_GWh,ExpectedAnnualLosses_GWh"])
for (n1,n2) in instance.BidirectionalArc:
    for i in instance.Period:
        my_string=str(n1)+","+str(n2)+","+str(value(2010+(i-1)*5))+","+str(value(instance.transmisionInvCap[n1,n2,i]))+","+str(value(instance.transmisionInstalledCap[n1,n2,i]))+","+ \
        str(value(instance.discount_multiplier[i]*instance.transmisionInvCap[n1,n2,i]*instance.transmissionInvCost[n1,n2,i]))+","+ \
        str(value(sum(instance.sceProbab[w]*instance.seasScale[s]*(instance.transmisionOperational[n1,n2,s,h,i,w]+instance.transmisionOperational[n2,n1,s,h,i,w])/1000 for (s,h) in instance.HoursOfSeason for w in instance.Scenario)))+","+ \
        str(value(sum(instance.sceProbab[w]*instance.seasScale[s]*((1 - instance.lineEfficiency[n1,n2])*instance.transmisionOperational[n1,n2,s,h,i,w] + (1 - instance.lineEfficiency[n2,n1])*instance.transmisionOperational[n2,n1,s,h,i,w])/1000 for (s,h) in instance.HoursOfSeason for w in instance.Scenario)))
        writer.writerow([my_string])
f.close()

f = open('results_output_Operational.csv', 'w', newline='')
writer = csv.writer(f)
writer.writerow(["Node,Period,Scenario,Season,Hour,Load_MW,Fossil_MW,Hydro_MW,RES_MW,Price_EuroPerMW,MargCO2factor_tonCO2perMW,EnergyLevel_MWh,NetDischarge_MW,LossesChargeDischarge_MW,NetFlowOut_MW,LossesFlowOut_MW,LoadShed_MW"])
for n in instance.Node:
    for i in instance.Period:
        for w in instance.Scenario:
            for (s,h) in instance.HoursOfSeason:
                my_string=str(n)+","+str(value(2010+(i-1)*5))+","+str(w)+","+str(s)+","+str(h)+","+ \
                str(value(instance.sload[n,s,h,i,w]))+","+ \
                str(value(sum(instance.genOperational[n,g,s,h,i,w] for g in instance.Generator if (n,g) in instance.GeneratorsOfNode and not ('Hydro',g) in instance.GeneratorsOfTechnology and not ('RES',g) in instance.GeneratorsOfTechnology)))+","+ \
                str(value(sum(instance.genOperational[n,g,s,h,i,w] for g in instance.Generator if (n,g) in instance.GeneratorsOfNode and ('Hydro',g) in instance.GeneratorsOfTechnology)))+","+ \
                str(value(sum(instance.genOperational[n,g,s,h,i,w] for g in instance.Generator if (n,g) in instance.GeneratorsOfNode and ('RES',g) in instance.GeneratorsOfTechnology or (n,g) in instance.GeneratorsOfNode and ('Hydro',g) in instance.GeneratorsOfTechnology)))+","+ \
                str(instance.dual[instance.FlowBalance[n,s,h,i,w]])+","+ \
                str(value(sum(instance.genOperational[n,g,s,h,i,w]*instance.genCO2factor[g,i] for g in instance.Generator if (n,g) in instance.GeneratorsOfNode)/sum(instance.genOperational[n,g,s,h,i,w] for g in instance.Generator if (n,g) in instance.GeneratorsOfNode)))+","+ \
                str(value(sum(instance.storOperational[n,b,s,h,i,w] for b in instance.Storage if (n,b) in instance.StoragesOfNode)))+","+ \
                str(value(sum(instance.storDischarge[n,b,s,h,i,w] - instance.storCharge[n,b,s,h,i,w] for b in instance.Storage if (n,b) in instance.StoragesOfNode)))+","+ \
                str(value(sum((1 - instance.storageDischargeEff[b])*instance.storDischarge[n,b,s,h,i,w] + (1 - instance.storageChargeEff[b])*instance.storCharge[n,b,s,h,i,w] for b in instance.Storage if (n,b) in instance.StoragesOfNode)))+","+ \
                str(value(sum(instance.transmisionOperational[n,outflow,s,h,i,w] for outflow in instance.NodesOut[n]) - sum(instance.transmisionOperational[inflow,n,s,h,i,w] for inflow in instance.NodesIn[n])))+","+ \
                str(value(sum((1 - instance.lineEfficiency[n,outflow])*instance.transmisionOperational[n,outflow,s,h,i,w] for outflow in instance.NodesOut[n])))+","+ \
                str(value(instance.loadShed[n,s,h,i,w]))
                writer.writerow([my_string])
f.close()

f = open('results_output_curtailed_prod.csv', 'w', newline='')
writer = csv.writer(f)
writer.writerow(["Node,GeneratorType,Period,ExpectedAnnualCurtailment_GWh"])
for (n,g) in instance.GeneratorsOfNode:
    if ('RES',g) in instance.GeneratorsOfTechnology and g != 'Bioexisting' and g != 'Bio' and g != 'Geo': 
        for i in instance.Period:
            my_string=str(n)+","+str(g)+","+str(value(2010+(i-1)*5))+","+ \
            str(value(sum(instance.sceProbab[w]*instance.seasScale[s]*(instance.genCapAvail[n,g,s,h,i,w]*instance.genInstalledCap[n,g,i] - instance.genOperational[n,g,s,h,i,w])/1000 for w in instance.Scenario for (s,h) in instance.HoursOfSeason)))#+","+ \
            writer.writerow([my_string])
f.close()

f = open('results_output_EuropePlot.csv', 'w', newline='')
writer = csv.writer(f)
writer.writerow(["Period,genInstalledCap_MW"])
my_string=""
for g in instance.Generator:
    my_string+=","+str(g)
writer.writerow([my_string])
for i in instance.Period:
    my_string=str(value(2010+(i-1)*5))
    for g in instance.Generator:
        my_string+=","+str(value(sum(instance.genInstalledCap[n,g,i] for n in instance.Node if (n,g) in instance.GeneratorsOfNode)))
    writer.writerow([my_string])
writer.writerow([""])
writer.writerow(["Period,genExpectedAnnualProduction_GWh"])
my_string=""
for g in instance.Generator:
    my_string+=","+str(g)
writer.writerow([my_string])
for i in instance.Period:
    my_string=str(value(2010+(i-1)*5))
    for g in instance.Generator:
        my_string+=","+str(value(sum(instance.sceProbab[w]*instance.seasScale[s]*instance.genOperational[n,g,s,h,i,w]/1000 for n in instance.Node if (n,g) in instance.GeneratorsOfNode for (s,h) in instance.HoursOfSeason for w in instance.Scenario)))
    writer.writerow([my_string])
writer.writerow([""])
writer.writerow(["Period,storPWInstalledCap_MW"])
my_string=""
for b in instance.Storage:
    my_string+=","+str(b)
writer.writerow([my_string])
for i in instance.Period:
    my_string=str(value(2010+(i-1)*5))
    for b in instance.Storage:
        my_string+=","+str(value(sum(instance.storPWInstalledCap[n,b,i] for n in instance.Node if (n,b) in instance.StoragesOfNode)))
    writer.writerow([my_string])
writer.writerow([""])
writer.writerow(["Period,storENInstalledCap_MW"])
my_string=""
for b in instance.Storage:
    my_string+=","+str(b)
writer.writerow([my_string])
for i in instance.Period:
    my_string=str(value(2010+(i-1)*5))
    for b in instance.Storage:
        my_string+=","+str(value(sum(instance.storENInstalledCap[n,b,i] for n in instance.Node if (n,b) in instance.StoragesOfNode)))
    writer.writerow([my_string])
writer.writerow([""])
writer.writerow(["Period,storExpectedAnnualDischarge_GWh"])
my_string=""
for b in instance.Storage:
    my_string+=","+str(b)
writer.writerow([my_string])
for i in instance.Period:
    my_string=str(value(2010+(i-1)*5))
    for b in instance.Storage:
        my_string+=","+str(value(sum(instance.sceProbab[w]*instance.seasScale[s]*instance.storDischarge[n,b,s,h,i,w]/1000 for n in instance.Node if (n,b) in instance.StoragesOfNode for (s,h) in instance.HoursOfSeason for w in instance.Scenario)))
    writer.writerow([my_string])
f.close()

f = open('results_output_EuropeSummary.csv', 'w', newline='')
writer = csv.writer(f)
writer.writerow(["Period,AvgExpectedCO2factor_TonPerMWh,AvgELPrice_EuroPerMWh,TotExpectedAnnualCurtailedRES_MWh,TotExpectedAnnualLossesChargeDischarge_GWh,ExpectedAnnualLossesTransmission_GWh"])
for i in instance.Period:
    my_string=str(value(2010+(i-1)*5))+","+ \
    str(value(sum(instance.sceProbab[w]*instance.genOperational[n,g,s,h,i,w]*instance.genCO2factor[g,i] for (n,g) in instance.GeneratorsOfNode for h in instance.Operationalhour for w in instance.Scenario)/sum(instance.sceProbab[w]*instance.genOperational[n,g,s,h,i,w] for (n,g) in instance.GeneratorsOfNode for h in instance.Operationalhour for w in instance.Scenario)))+","+ \
    str(value(sum(instance.sceProbab[w]*instance.dual[instance.FlowBalance[n,s,h,i,w]] for n in instance.Node for (s,h) in instance.HoursOfSeason for w in instance.Scenario)/value(len(instance.HoursOfSeason)*len(instance.Node))))+","+ \
    str(value(sum(instance.sceProbab[w]*instance.seasScale[s]*(instance.genCapAvail[n,g,s,h,i,w]*instance.genInstalledCap[n,g,i] - instance.genOperational[n,g,s,h,i,w]) for (n,g) in instance.GeneratorsOfNode if ('RES',g) in instance.GeneratorsOfTechnology for w in instance.Scenario for (s,h) in instance.HoursOfSeason)))+","+ \
    str(value(sum(instance.sceProbab[w]*instance.seasScale[s]*((1 - instance.storageDischargeEff[b])*instance.storDischarge[n,b,s,h,i,w] + (1 - instance.storageChargeEff[b])*instance.storCharge[n,b,s,h,i,w])/1000 for (n,b) in instance.StoragesOfNode for (s,h) in instance.HoursOfSeason for w in instance.Scenario)))+","+ \
    str(value(sum(instance.sceProbab[w]*instance.seasScale[s]*((1 - instance.lineEfficiency[n1,n2])*instance.transmisionOperational[n1,n2,s,h,i,w] + (1 - instance.lineEfficiency[n2,n1])*instance.transmisionOperational[n2,n1,s,h,i,w])/1000 for (n1,n2) in instance.BidirectionalArc for (s,h) in instance.HoursOfSeason for w in instance.Scenario)))
    writer.writerow([my_string])
writer.writerow([""])
writer.writerow(["GeneratorType,Period,genInvCap_MW,genInstalledCap_MW,TotDiscountedInvestmentCost_EuroPerMW,genExpectedAnnualProduction_GWh"])
for g in instance.Generator:
    for i in instance.Period:
        my_string=str(g)+","+str(value(2010+(i-1)*5))+","+str(value(sum(instance.genInvCap[n,g,i] for n in instance.Node if (n,g) in instance.GeneratorsOfNode)))+","+ \
        str(value(sum(instance.genInstalledCap[n,g,i] for n in instance.Node if (n,g) in instance.GeneratorsOfNode)))+","+ \
        str(value(sum(instance.discount_multiplier[i]*instance.genInvCap[n,g,i]*instance.genInvCost[g,i] for n in instance.Node if (n,g) in instance.GeneratorsOfNode))) +","+ \
        str(value(sum(instance.seasScale[s]*instance.sceProbab[w]*instance.genOperational[n,g,s,h,i,w]/1000 for n in instance.Node if (n,g) in instance.GeneratorsOfNode for (s,h) in instance.HoursOfSeason or w in instance.Scenario)))       
        writer.writerow([my_string])
writer.writerow([""])
writer.writerow(["StorageType,Period,storPWInvCap_MW,storPWInstalledCap_MW,storENInvCap_MWh,storENInstalledCap_MWh,TotDiscountedInvestmentCostPWEN_EuroPerMWMWh,ExpectedAnnualDischargeVolume_GWh"])
for b in instance.Storage:
    for i in instance.Period:
        my_string=str(b)+","+str(value(2010+(i-1)*5))+","+str(value(sum(instance.storPWInvCap[n,b,i] for n in instance.Node if (n,b) in instance.StoragesOfNode)))+","+ \
        str(value(sum(instance.storPWInstalledCap[n,b,i] for n in instance.Node if (n,b) in instance.StoragesOfNode)))+","+ \
        str(value(sum(instance.storENInvCap[n,b,i] for n in instance.Node if (n,b) in instance.StoragesOfNode)))+","+ \
        str(value(sum(instance.storENInstalledCap[n,b,i] for n in instance.Node if (n,b) in instance.StoragesOfNode)))+","+ \
        str(value(sum(instance.discount_multiplier[i]*(instance.storPWInvCap[n,b,i]*instance.storPWInvCost[b,i] + instance.storENInvCap[n,b,i]*instance.storENInvCost[b,i]) for n in instance.Node if (n,b) in instance.StoragesOfNode)))+","+ \
        str(value(sum(instance.seasScale[s]*instance.sceProbab[w]*instance.storDischarge[n,b,s,h,i,w]/1000 for n in instance.Node if (n,b) in instance.StoragesOfNode for (s,h) in instance.HoursOfSeason or w in instance.Scenario)))
        writer.writerow([my_string])
f.close()
