import heapq
import random as rand

class Node:
    def __init__(self, parent):
        self.accuracy = 0.0 # calls eval 
        self.parent = parent
        self.currentFeatures = [] # forward + backward (Passed in features through main)

    def __lt__(self, other):
      return self.accuracy < other.accuracy

    def printInfo(self):
      print("Using feature(s) ", self.currentFeatures," accuracy is ", round(self.accuracy, 2))


class Problem:
    def __init__(self, features) -> None:
      self.nodequeue = [] #this will be a max heapq
      self.features = features
      self.seen = []
      self.overallMaxAccuracy = 0
      self.bestNode = Node(self)

    def eval(self, classifier, validator, feature_set, k):
      return validator.leave_one_out(classifier, feature_set, k)

    def greedy_backward_search(self, classifier, validator, k=1):
      #initialize node with all the features 
      root = Node(None) 
      root.accuracy = self.eval(classifier, validator, list(self.features), k)
      root.currentFeatures = self.features # all the features

      # add root to the queue (sort by max accuracy)
      heapq.heappush(self.nodequeue, (-root.accuracy, root)) 

      # add root to seen list
      if root:
        self.seen.append(root.currentFeatures)
        #print("Using all feature(s) ",root.currentFeatures," accuracy is ",round(root.accuracy, 2))
        root.printInfo()
      else:
        ValueError("root is None!!")

      parent = root
      currMaxAccuracy = 0.01
      bestFeatures = None
          
      #while there are still features to be eliminated
      while parent.currentFeatures:
        pair = heapq.heappop(self.nodequeue) # pair is (-accuracy, node)
        currMaxAccuracy = -pair[0] # make it positive (double negative)
        parent = pair[1]
        self.overallMaxAccuracy = max(self.overallMaxAccuracy, currMaxAccuracy)
        
        childMax = 0
        if(self.overallMaxAccuracy == currMaxAccuracy):
          self.bestNode = pair[1]
        
        for feature in parent.currentFeatures:
          newNode = Node(parent)
          newNode.accuracy = self.eval(classifier, validator, feature, k)
          childMax = max(childMax, newNode.accuracy)
          # give child node currentFeatures of its parent
          newNode.currentFeatures = list(newNode.parent.currentFeatures)
          newNode.currentFeatures.remove(feature) # remove one feature for child node

          # print accuracy of each feature
          newNode.printInfo()
          
          #skip node if seen
          if newNode.currentFeatures in self.seen:
            continue

          #push each node into heap, where each node is a diff combination of features
          heapq.heappush(self.nodequeue, (-newNode.accuracy, newNode))
          self.seen.append(newNode.currentFeatures) # add to seen list
          
          
          if(newNode.accuracy >= self.overallMaxAccuracy):
            self.bestNode = newNode
            self.overallMaxAccuracy = newNode.accuracy
            

        bestFeatures = self.bestNode.currentFeatures

        if childMax<parent.accuracy:
          print("Warning! accuracy has decreased!So we stop searching..")
          print("Feature set ", bestFeatures, " was best, accuracy is ", round(self.overallMaxAccuracy, 2), "%")
          break
        #compare accuracies of current subset and output best accuracy
        print("Feature set ", bestFeatures, " was best, accuracy is ", round(self.overallMaxAccuracy, 2), "%")
      
      return bestFeatures
  
    def greedy_forward_search(self, classifier, validator, k=1):
        result = [set()]
        best_score = 0.0 #current total evaluation for the subset

        available_features = set(self.features)  # Use a set for available features

        while available_features:
            curr_best_score = 0.0
            curr_best_feature = None

            for feature in available_features:
                # eval feature with most recent subset
                current_set = result[-1] | {feature}
                curr_score = self.eval(classifier, validator, list(current_set), k)
                print("Using feature(s) ", result[-1] | {feature}  ," accuracy is ", round(curr_score, 2))
                if curr_score > curr_best_score:
                    curr_best_score = curr_score
                    curr_best_feature = feature

            if best_score <= curr_best_score:
                best_score = curr_best_score  # update the current best score
                new_best_set = result[-1] | {curr_best_feature}
                available_features.remove(curr_best_feature) # remove the best feature from the features 
                result.append(new_best_set)  # add the new best subset
                print("Feature set ", result[-1], " was best, accuracy is ", round(best_score, 2), "%")

            else:
                print("Warning! accuracy has decreased! So we stop searching..")
                print("Feature set ", result[-1], " was best, accuracy is ", round(best_score, 2), "%")
                return result[-1]
        
        return result[-1] 
   

    def bidirectional_feature_selection(self, classifier, validator, max_iter=100, k =1):
      n_features = len(self.features)
      selected_features = []
      remaining_features = list(range(n_features))
      best_score = float('-inf')
      improved = True
      iteration = 0
      print(remaining_features)
      while improved and iteration < max_iter:
          improved = False
          iteration += 1

          # Forward Step
          forward_best_score = best_score
          forward_best_feature = None
          for feature in remaining_features:
              temp_features = selected_features + [feature]
              score = self.eval(classifier, validator, list(temp_features), k)
              if score > forward_best_score:
                  forward_best_score = score
                  forward_best_feature = feature

          if forward_best_feature is not None:
              selected_features.append(forward_best_feature)
              remaining_features.remove(forward_best_feature)
              best_score = forward_best_score
              improved = True
              print("Feature set ", selected_features[-1], " was best, accuracy is ", round(best_score, 2), "%")

          # Backward Step
          backward_best_score = best_score
          backward_worst_feature = None
          for feature in selected_features:
              temp_features = list(selected_features)
              temp_features.remove(feature)
              if not temp_features:  # Skip if no features left after removal
                  continue
              score = self.eval(classifier, validator, list(temp_features), k)
              if score > backward_best_score:
                  backward_best_score = score
                  backward_worst_feature = feature

          if backward_worst_feature is not None:
              selected_features.remove(backward_worst_feature)
              remaining_features.append(backward_worst_feature)
              best_score = backward_best_score
              improved = True

      return selected_features