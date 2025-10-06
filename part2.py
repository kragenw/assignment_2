import robby
import GAinspector
#import numpy as np
from utils import *
import random
import heapq
POSSIBLE_ACTIONS = ["MoveNorth", "MoveSouth", "MoveEast", "MoveWest", "StayPut", "PickUpCan", "MoveRandom"]
PAUSE = 0.08
CYCLE_LIMIT = 3
FAST_STEPS = 200
rw = robby.World(10, 10)
rw.graphicsOff()


def sortByFitness(genomes):
    tuples = [(fitness(g), g) for g in genomes]
    tuples.sort()
    sortedFitnessValues = [f for (f, g) in tuples]
    sortedGenomes = [g for (f, g) in tuples]
    return sortedGenomes, sortedFitnessValues


def randomGenome(length):
    """
    :param length:
    :return: string, random integers between 0 and 6 inclusive
    """

    return "".join(random.choice("0123456") for _ in range(length))



def makePopulation(size, length):
    """
    :param size - of population:
    :param length - of genome
    :return: list of length size containing genomes of length length
    """


    return [randomGenome(length) for _ in range(size)]

fitness_cache = {}

def fitness(genome, steps=200, init=0.50):
    """

    :param genome: to test
    :param steps: number of steps in the cleaning session
    :param init: amount of cans
    :return:
    """
    if type(genome) is not str or len(genome) != 243:
        raise Exception("strategy is not a string of length 243")
    for char in genome:
        if char not in "0123456":
            raise Exception("strategy contains a bad character: '%s'" % char)
    if type(steps) is not int or steps < 1:
        raise Exception("steps must be an integer > 0")
    if type(init) is str:
        # init is a config file
        rw.load(init)
    elif type(init) in [int, float] and 0 <= init <= 1:
        # init is a can density
        rw.goto(0, 0)
        rw.distributeCans(init)
    else:
        raise Exception("invalid initial configuration")

    if genome in fitness_cache:
        return fitness_cache[genome]

    all_scores = 0
    # rw.graphicsOn()
    for trial in range(25):
        score = 0
        for i in range(steps):
            p = rw.getPerceptCode()
            # print("the code is: ", p)
            action = POSSIBLE_ACTIONS[int(genome[p])]
            # print("action is: ", action)
            score += rw.performAction(action)
            
            
            
        #     if not cycleDetected:
        #         # skip after having detected a cycle
        #         state = [action, rw.robbyRow, rw.robbyCol, rw._gridContents()]
        #         if action != "MoveRandom":
        #             period = rw._checkForCycle(state, history, CYCLE_LIMIT)
        #             if period > 0:
        #                 print("Cycle detected! period: ", period)
        #                 cycleDetected = True
        #                 if period == 1:
        #                     runFastUntil = i + FAST_STEPS/2
        #                 else:
        #                     runFastUntil = i + FAST_STEPS
        #         history.append(state)
        #     elif rw.graphicsEnabled and i > runFastUntil:
        #         # disable graphics after running for FAST_STEPS
        #         rw.graphicsEnabled = False
        # if not rw.graphicsEnabled:
        #     rw.graphicsEnabled = True
        #     rw._updateGrid()
        
        
        all_scores += score
        rw.goto(0, 0)
        rw.distributeCans()
        
    result = all_scores / 25.0
    fitness_cache[genome] = result
    return result    
    

def evaluateFitness(population):
    """
    :param population:
    :return: a pair of values: the average fitness of the population as a whole and the fitness of the best individual
    in the population.
    """
    # TODO: you might be fucked by returning another variable
    scores = [fitness(genome) for genome in population]
    return (sum(scores)/len(scores), max(scores), scores)


def crossover(genome1, genome2):
    """
    :param genome1:
    :param genome2:
    :return: two new genomes produced by crossing over the given genomes at a random crossover point.
    """
    
    # print("Before Crossover: \n", genome1, genome2)
    
    if len(genome1) != len(genome2):
        print("ts aint gon work cuh")
        return False
    crossover_p = random.randint(1,len(genome1) - 1)
    # print("Crossover Point: ", crossover_p)

    # print("After Crossover: \n", genome1[:crossover_p] + genome2[crossover_p:], genome2[:crossover_p] + genome1[crossover_p:])
    return genome1[:crossover_p] + genome2[crossover_p:], genome2[:crossover_p] + genome1[crossover_p:]

ALT = {c: [x for x in "0123456" if x != c] for c in "0123456"}

def mutate(genome, mutationRate):
    """
    :param genome:
    :param mutationRate:
    :return: a new mutated version of the given genome.
    """
    g = list(genome)
    for i in range(len(g)):
        if random.random() <= mutationRate:
            g[i] = random.choice(ALT[g[i]])
    return "".join(g)

def selectPair(population):
    """

    :param population:
    :return: two genomes from the given population using fitness-proportionate selection.
    This function should use RankSelection,
    """
    
    # TODO: you might be fucked by assuming that scores is in the same order as population
    # Also keep in mind I'm adding another instance variable to the function
    # not population comes in sorted

    
    multiplier = 5  # Adjust this multiplier to control the proportionality
    ranks = list(range(1, len(population) + 1))
    total_rank = sum(r * multiplier for r in ranks)
    probabilities = [(r * multiplier / total_rank) * 100 for r in ranks]
    
    # for thing in paired:
    #     print(f"{thing[0]}, {thing[1][:5]}")


    selected1 = weightedChoice(population, probabilities)
    selected2 = weightedChoice(population, probabilities)

    # print(f"Selected: {selected1[:5]}, {selected2[:5]}")

    return selected1, selected2
    
    
def runGA(populationSize, crossoverRate, mutationRate, logFile=""):
    """

    :param populationSize: :param crossoverRate: :param mutationRate: :param logFile: :return: xt file in which to
    store the data generated by the GA, for plotting purposes. When the GA terminates, this function should return
    the generation at which the string of all ones was found.is the main GA program, which takes the population size,
    crossover rate (pc), and mutation rate (pm) as parameters. The optional logFile parameter is a string specifying
    the name of a te
    """
    
    print(f"Population Size: {populationSize}\n")
        
    generation = makePopulation(populationSize, 243)
    
    with open(logFile, "w") as f:
        f.write("PopulationSize: {0}, CrossoverRate: {1}, MutationRate: {2}\n".format(populationSize, crossoverRate, mutationRate))
    printProgressBar(0, 301, prefix = 'Progress:', suffix = 'Complete', length = 50)
    for i in range(1001):
        score, best, scores = evaluateFitness(generation)
        # with open(logFile, "a") as f:
        #     f.write(f"{i} {round(score, 2)} {best}\n")
        if i % 10 == 0:
            # print(f"Population Size: {populationSize}, Generation {i}: Avg Fitness {round(score, 2)}, Best Fitness {best}")
            generation_number = i
            average_fitness = round(score, 2)
            best_fitness = round(best, 2)
            best_genome = generation[scores.index(best)]
            # print(f"Generation Number: {generation_number}, Average Fitness: {average_fitness}, Best Fitness: {best_fitness}, Genome: {best_genome}")
            with open(logFile, "a") as f:
                f.write(f"{generation_number}\t{average_fitness}\t{best_fitness}\t{best_genome}\n")

        paired = list(zip(scores, generation))
        paired.sort()
        sorted_genomes = [g for (_, g) in paired]
        
        pairs = [(selectPair(sorted_genomes)) for _ in range(populationSize//2)]
        crossed = [crossover(pair[0], pair[1]) for pair in pairs if random.uniform(0, 1) <= crossoverRate]
        new_generation = []
        for cross in crossed:
            new_generation.append(mutate(cross[0], mutationRate))
            new_generation.append(mutate(cross[1], mutationRate))
        generation = new_generation

        printProgressBar(i + 1, 301, prefix = 'Progress:', suffix = 'Complete', length = 50)

    return False


def test_FitnessFunction():
    f = fitness(rw.strategyM)
    print("Fitness for StrategyM : {0}".format(f))

def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
    # Print New Line on Complete
    if iteration == total: 
        print()
        
        
def testGA():
    """
    Runs the genetic algorithm multiple times and writes the results to a single file.

    :return: None
    """
    
    # this told me that a crossover of 1, mutation of 0.01, and population of 1000 was best
    
    population_sizes = [100, 200, 500, 1000]
    crossover_rates = [0.7, 1.0]
    mutation_rates = [0.0001, 0.0005, 0.001, 0.005, 0.01]

    for pop in population_sizes:
        log_file = f"GA_results_population_{pop}.txt"
        runGA(pop, 0.7, 0.001, logFile=log_file)
    for cross in crossover_rates:
        log_file = f"GA_results_crossover_{cross}.txt"
        runGA(100, cross, 0.001, logFile=log_file)

    for mut in mutation_rates:
        log_file = f"GA_results_mutation_{mut}.txt"
        runGA(100, 0.7, mut, logFile=log_file)


if __name__ == '__main__':
    
    # testGA()
    
    runGA(1000, 1, 0.01, logFile="HyperOptimized.txt")
            
    # test_FitnessFunction()

    #runGA(100, 1.0, 0.05)