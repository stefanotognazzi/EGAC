from __future__ import print_function



import random



from deap import base

from deap import creator

from deap import tools

from py4j.java_gateway import JavaGateway, GatewayParameters

#from sets import Set





# Link to the java gateway and load the CRN



#netName = "CRNNetworks/NCC_AM.crn"

#n = gateway.entry_point.loadCRN(netName) # n is the number of species



# Let us create some auxiliary data structure needed in order to correcly call the computeBB

#function within the Java ERODE tool

 # not necessary total number of species of the source network 



 # number of all target species of the target network  (2 species, 4 targets x0 x2 y0 y2)

 # number of possible tuples of the target network 



post = []









def genPost(n):

    spec = n*3

    post = [0]*spec

    for i in range(n):

        post[i*3] = i*2

        post[(i*3)+1] = i*2 + 1

        post[(i*3)+2] = - (i*2 + 1)

    return post 



def ind2par(indiv):

    spec = 3*len(indiv)

    mid = [0]*spec

    for i in range(len(indiv)):

        mid[i*3] = indiv[i]

        if indiv[i] % 2 == 0:

            mid[(i*3)+1] = indiv[i] +1

            mid[(i*3)+2] = - (indiv[i]+1)

        else: 

            mid[(i*3)+1] = indiv[i] -1

            mid[(i*3)+2] = - indiv[i]

    ret = mid + post

    return ret



def certFit(indiv):

    ret = 100

    aux = ind2par(indiv)

    for i in range(len(aux)):

        int_array[i] = aux[i]

    hi = gateway.entry_point.computeBB(int_array,False)

    ret = len(set(hi))

    aa = []

    for i in range(len(indiv)):

        aa.append(indiv[i])    

        if aa[i]%2 == 1:

            aa[i] = aa[i] - 1

    if len(set(aa)) < K:

        ret = 100

    return ret,



##
## main
##
## PARAMETERS:
## netName: input file containing the union of the source and target network
## srcTup: number of triplets in the source network
## trgTup: number of triplets in the target network
## NPOP: size of the population
## NGEN: number of generations
## cx: corssover probability
## mut: mutation probability
## seed: starting random seed
## Log : output file (SEE USAGE EXAMPLE)
## nport: Java gateway port number (SEE USAGE EXAMPLE)


def main(netName,srcTup,trgTup,NPOP,NGEN,cx,mut,seed,log,nport):

    global gateway 

    

    gateway = JavaGateway(gateway_parameters=GatewayParameters(port=nport))

    n = gateway.entry_point.loadCRN(netName) # n is the number of species

    #n = 39

    global K

    K = trgTup  #Number of tuples target

    k = K*2

    M = srcTup  #Number of tuples source

    m = M * 3

    FITLIMIT = K * 3

    int_class = gateway.jvm.int

    global int_array 

    int_array = gateway.new_array(int_class,n)

    #log = open("goat.txt", "w")

    #print("test", file = log)

    

    creator.create("FitnessMin", base.Fitness, weights=(-1.0,))

    creator.create("Individual", list, fitness=creator.FitnessMin)



    toolbox = base.Toolbox()



    toolbox.register("attr_bool", random.randint, 0, (k-1)) # k blocks



    toolbox.register("individual", tools.initRepeat, creator.Individual,toolbox.attr_bool, M)  



    toolbox.register("population", tools.initRepeat, list, toolbox.individual)

    

    toolbox.register("evaluate", certFit)



# register the crossover operator

    toolbox.register("mate", tools.cxTwoPoint)



    toolbox.register("mutate", tools.mutFlipBit, indpb=0.1)



    toolbox.register("select", tools.selTournament, tournsize=3)

    

    

    global post 

    post = genPost(K)

    

    random.seed(seed)

    pop = toolbox.population(NPOP)

    #print pop

    CX = cx

    #NGEN = 20

    MUT = mut

    print("Start %s " % seed , file=log )

    #fitnesses = list(map(toolbox.evaluate,pop))

    fitnesses = list(map(toolbox.evaluate, pop))

    #print zip(pop,fitnesses)

    for ind, fit in zip(pop, fitnesses):

        ind.fitness.values = fit

    #print fitnesses

    for g in range(NGEN):

        offspring = toolbox.select(pop, len(pop))

        # Clone the selected individuals

        offspring = list(map(toolbox.clone, offspring))

        for child1, child2 in zip(offspring[::2], offspring[1::2]):



            # cross two individuals with probability CXPB

            if random.random() < CX:

                toolbox.mate(child1, child2)



                # fitness values of the children

                # must be recalculated later

                del child1.fitness.values

                del child2.fitness.values

                

        for mutant in offspring:

            # mutate an individual with probability MUTPB

            if random.random() < MUT:

                #toolbox.mutate(mutant)

                j = random.randint(0,len(mutant)-1)

                l = random.randint(0,len(mutant)-1)

                sw = mutant[l]

                mutant[l] = mutant[j]

                mutant[j] = sw

                del mutant.fitness.values

                ####LET'S TRY OUR MUTATION SWAP RATHER THEN THE DEFAULT ONE

                

        pop[:] = offspring

        fitnesses = map(toolbox.evaluate, pop)

        #print fitnesses

        for ind, fit in zip(pop, fitnesses):

            ind.fitness.values = fit

        

        #print("  Evaluated %i individuals" % len(invalid_ind))

        

        

    

        

        fits = [ind.fitness.values[0] for ind in pop]

        

        length = len(pop)

        #mean = sum(fits) / length

        #sum2 = sum(x*x for x in fits)

        #std = abs(sum2 / length - mean**2)**0.5

        

        print("  Min %s" % min(fits) , file = log )

        print("  Min %s" % min(fits))

        print("  Max %s" % max(fits))

        #print("  Avg %s" % mean)

        #print("  Std %s" % std)  

        #if min(fits) == FITLIMIT:

        #    break

    best_ind = tools.selBest(pop, 1)[0]

    print(best_ind ,file = log)

    print(best_ind.fitness.values , file = log)

    #print toolbox.evaluate(best_ind)

    #print(pop)

    fitnesses = map(toolbox.evaluate, pop)

    #print fitnesses

    emulations = []

    for ind, fit in zip(pop, fitnesses):

        if fit == (FITLIMIT,):

            emulations.append(ind)

    #print emulations 

    x = {tuple(x) for x in emulations}

    print(x , file = log)

    print(x)