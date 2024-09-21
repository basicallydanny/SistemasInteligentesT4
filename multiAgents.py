# multiAgents.py
# --------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).

from math import dist
from util import manhattanDistance
from game import Directions
import random, util

from game import Agent
from pacman import GameState

class ReflexAgent(Agent):
    """
      A reflex agent chooses an action at each choice point by examining
      its alternatives via a state evaluation function.

      The code below is provided as a guide.  You are welcome to change
      it in any way you see fit, so long as you don't touch our method
      headers.
    """
    def getAction(self, gameState):
        """
        You do not need to change this method, but you're welcome to.

        getAction chooses among the best options according to the evaluation function.

        Just like in the previous project, getAction takes a GameState and returns
        some Directions.X for some X in the set {North, South, West, East, Stop}
        """
        # Collect legal moves and successor states
        legalMoves = gameState.getLegalActions()

        # Choose one of the best actions
        scores = [self.evaluationFunction(gameState, action) for action in legalMoves]
        bestScore = max(scores)
        bestIndices = [index for index in range(len(scores)) if scores[index] == bestScore]
        chosenIndex = random.choice(bestIndices) # Pick randomly among the best

        "Add more of your code here if you want to"

        return legalMoves[chosenIndex]

# DANIELA 
    def evaluationFunction(self, currentGameState, action):
        """
        Design a better evaluation function here.

        The evaluation function takes in the current and proposed successor
        GameStates (pacman.py) and returns a number, where higher numbers are better.

        The code below extracts some useful information from the state, like the
        remaining food (newFood) and Pacman position after moving (newPos).
        newScaredTimes holds the number of moves that each ghost will remain
        scared because of Pacman having eaten a power pellet.

        Print out these variables to see what you're getting, then combine them
        to create a masterful evaluation function.
        """
        # Useful information you can extract from a GameState (pacman.py)
        successorGameState = currentGameState.generatePacmanSuccessor(action)
        
        "*** YOUR CODE HERE ***"
        ghostDist = self.distanceToGhost(successorGameState)
        foodDist = self.distanceToFood(successorGameState, currentGameState)
        return ghostDist / (foodDist + 1) #si no hay comida

        # Más lejos de los fantasmas y más cerca de la comida, escalo
        # las distancias en valores comparables

    def distanceToGhost(self, gameState):
        pacmanPos = gameState.getPacmanPosition()
        ghostsPos = gameState.getGhostPositions()
        distances = [dist(pacmanPos, ghostPos) for ghostPos in ghostsPos]
        return min(distances)

    def distanceToFood(self, nextState, currentState):
        pacmanPos = nextState.getPacmanPosition()
        foodsPos = currentState.getFood().asList()
        distances = [dist(pacmanPos, foodPos) for foodPos in foodsPos]
        return min(distances)

def scoreEvaluationFunction(currentGameState):
    """
      This default evaluation function just returns the score of the state.
      The score is the same one displayed in the Pacman GUI.

      This evaluation function is meant for use with adversarial search agents
      (not reflex agents).
    """
    return currentGameState.getScore()

class MultiAgentSearchAgent(Agent):
    """
      This class provides some common elements to all of your
      multi-agent searchers.  Any methods defined here will be available
      to the MinimaxPacmanAgent, AlphaBetaPacmanAgent & ExpectimaxPacmanAgent.

      You *do not* need to make any changes here, but you can if you want to
      add functionality to all your adversarial search agents.  Please do not
      remove anything, however.

      Note: this is an abstract class: one that should not be instantiated.  It's
      only partially specified, and designed to be extended.  Agent (game.py)
      is another abstract class.
    """

    def __init__(self, evalFn = 'scoreEvaluationFunction', depth = '2'):
        self.index = 0 # Pacman is always agent index 0
        self.evaluationFunction = util.lookup(evalFn, globals())
        self.depth = int(depth)

# DANIELA
class MinimaxAgent(MultiAgentSearchAgent):
    """
    Minimax agent focusing only on Pacman (no ghosts).
    """
    def getAction(self, gameState: GameState):
        """
        Returns the minimax action from the current gameState using self.depth
        and self.evaluationFunction.
        """
        action, _ = self.minimax(gameState, 0)
        return action
    def minimax(self, gameState, depth):
        # Ganamos, Perdiomos, o podemos continuar
        if gameState.isWin() or gameState.isLose() or depth == self.depth:
            return None, self.evaluationFunction(gameState)
        # movimientos de Pacman
        pacMoves = gameState.getLegalActions(0)
        # Evaluar todos los sucesores de Pac recursivamente
        bestAct = None
        bestVal = float("-inf")
        for action in pacMoves:
            nextState = gameState.generateSuccessor(0, action)
            _, val = self.minimax(nextState, depth + 1)
            # Maximizar el valor
            if val > bestVal:
                bestVal = val
                bestAct = action
        return bestAct, bestVal

class AlphaBetaAgent(MultiAgentSearchAgent):
    """
      Your minimax agent with alpha-beta pruning (question 3)
    """

    def getAction(self, gameState):
        """
          Returns the minimax action using self.depth and self.evaluationFunction
        """
        "*** YOUR CODE HERE ***"
        return None

class ExpectimaxAgent(MultiAgentSearchAgent):
    """
      Your expectimax agent (question 4)
    """
    def getAction(self, gameState):
        """
          Returns the expectimax action using self.depth and self.evaluationFunction

          All ghosts should be modeled as choosing uniformly at random from their
          legal moves.
        """
        "*** YOUR CODE HERE ***"
        action, _ = self.expectimax(gameState, 0, 0)
        return action
    def expectimax(self, game_state, agent_index, depth):
            return None

# DANIELA 
def betterEvaluationFunction(currentGameState):
    """
    An improved evaluation function that assesses the desirability of the current
    game state based on Pacman's position relative to food, ghosts, and capsules.

    DESCRIPTION: Esta función calcula la distancia a la comida más cercana, la distancia 
    total a los fantasmas, la proximidad de los fantasmas y cuenta la cantidad
    de capsulas de poder disponibles. 
    """
    # Pacman
    pacmanPos = currentGameState.getPacmanPosition()
    # Comida y su distancia
    foodList = currentGameState.getFood().asList()
    minFoodDist = min(util.manhattanDistance(pacmanPos, food) for food in foodList) if foodList else 0
    # Fantasmas y su distancia
    ghostPositions = currentGameState.getGhostPositions()
    distancesToGhosts = sum(util.manhattanDistance(pacmanPos, ghost) for ghost in ghostPositions)
    proximityToGhosts = sum(1 for ghost in ghostPositions if util.manhattanDistance(pacmanPos, ghost) <= 1)
    # Get the number of capsules available
    capNum = len(currentGameState.getCapsules())
    # Mejor
    score = (
        currentGameState.getScore() +
        (1 / float(minFoodDist + 1)) -
        (1 / float(distancesToGhosts + 1)) -
        proximityToGhosts -
        capNum
    )
    return score

# Abbreviation
better = betterEvaluationFunction