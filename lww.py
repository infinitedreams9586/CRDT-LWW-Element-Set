import time

class Element:
    """
    Element class
    :parameter
        item : any item
        timestamp (int, optional): timestamp
    """
    def __init__(self, item, timestamp=None):
        self.item = item
        self.timestamp = time.time() if not timestamp else timestamp

    def __str__(self):
        return "{0}:{1}".format(self.item, self.timestamp)

    def __repr__(self):
        return self.__str__()


class TwoPhaseSet:
    """
    2P-Set (Two-Phase Set)
    Two Phase set includes remove set. Elements can be added and also removed.
    Once removed, an element can not be re-added.
    2P-set uses "remove wins" semantics.
    """
    def __init__(self):
        self.AddSet = {}
        self.RemoveSet = {}

    def lookup_element(self, e):
        """
        Checks if element is in RemoveSet or not
        :param e (element): Instance of Element
        :return (bool): True if element is in RemoveSet, False otherwise
        """
        return True if e.item not in self.RemoveSet.keys() else False

    def get_resultant_document(self):
        """
        Generates resultant list of items after evaluating AddSet and RemoveSet
        :return (list of elements): Resultant list of elements
        """
        result = []
        for k, v in self.AddSet.items():
            e = Element(k, v)
            if self.lookup_element(e):
                result.append(e)
        return result

    def add(self, e):
        """
        Adds element in AddSet after evaluating timestamp
        :param e (element): Instance of Element
        :return: None
        """
        if e.item in self.AddSet.keys():
            ts = self.AddSet[e.item]
            if ts < e.timestamp:
                self.AddSet[e.item] = e.timestamp
        else:
            self.AddSet[e.item] = e.timestamp

    def remove(self, e):
        """
        Adds element in RemoveSet if not already
        :param e : Instance of Element
        :return: None
        """
        if self.lookup_element(e):
            self.RemoveSet[e.item] = e.timestamp

    def create_element(self, k, v):
        """
        Creates an instance of Element out of Key and Value supplied.
        :param k: Key (Item)
        :param v: Value (Timestamp)
        :return: An instance of Element
        """
        e = Element(k, v)
        return e

    def __add__(self, other):
        """
        Override Add operator
        :param other: Instance of the same class
        :return: New instance of the same class
        """
        result = self.__class__()
        for k, v in self.AddSet.items():
            result.add(self.create_element(k, v))

        for k, v in other.AddSet.items():
            result.add(self.create_element(k, v))

        for k, v in self.RemoveSet.items():
            result.remove(self.create_element(k, v))

        for k, v in other.RemoveSet.items():
            result.remove(self.create_element(k, v))

        return result

    def __repr__(self):
        """
        String representation of the instance
        :return: string in the format 'AddSet:RemoveSet'
        """
        return "{0}:{1}".format(self.AddSet, self.RemoveSet)


class LWWElementSet(TwoPhaseSet):
    """
    LWW-Element-Set is similar to 2P_Set with a timestamp for each element.
    An element is a member of the set if it is in AddSet and either not in RemoveSet or
    in the RemoveSet but with an earlier timestamp than the latest timestamp.
    """
    def __init__(self):
        super(LWWElementSet, self).__init__()

    def lookup_element(self, e):
        """
        An element is a member if it is in AddSet and either not in RemoveSet or
        in the RemoveSet but with an earlier timestamp than the latest timestamp.
        :param e: Instance of Element
        :return (bool): True if condition is met, False otherwise.
        """
        if e.item in self.RemoveSet.keys():
            curr = self.RemoveSet[e.item]
            if e.timestamp > curr:
                return True

        if e.item in self.AddSet.keys() and e.item not in self.RemoveSet.keys():
            return True

        return True if e.item not in self.RemoveSet.keys() else False


