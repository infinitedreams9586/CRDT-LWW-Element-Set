from unittest import TestCase
from lww import Element, LWWElementSet

class TestLWWElementSet(TestCase):
    """
    LWW-Element-Set Test Class
    """
    def setUp(self):
        """
        Initial setup
        """
        # Create some elements with value and timestamp
        self.e1 = Element(1, 1111)
        self.e2 = Element(2, 2222)
        self.e3 = Element(3, 3333)

        self.e10 = Element(1, 1234)
        self.e11 = Element(2, 2345)
        self.e12 = Element(3, 3456)


    def test_should_add_remove_elements(self):
        """
        Test should add and remove elements in LWW-Element-Set
        """
        # Add: {1:1111, 2:2222} Remove: {3:3333}
        lww_set = LWWElementSet()
        lww_set.add(self.e1)
        lww_set.add(self.e2)

        lww_set.remove(self.e3)

        self.assertTrue(lww_set.lookup_element(self.e1))
        self.assertTrue(lww_set.lookup_element(self.e2))

        self.assertFalse(lww_set.lookup_element(self.e3))

    def test_should_add_latest_element_if_added_after_removal(self):
        """
        Test should add latest element in the AddSet, if older one is in RemoveSet
        """
        # Add: {1:1111, 2:2222} Remove: {1:1111}
        lww_set = LWWElementSet()
        lww_set.add(self.e1)
        lww_set.add(self.e2)

        lww_set.remove(self.e1)
        # Add new latest new_e1 element with new timestamp
        new_e1 = Element(1, 1112)
        # Add: {1:1112}
        lww_set.add(new_e1)

        self.assertFalse(lww_set.lookup_element(self.e1))

        self.assertTrue(lww_set.lookup_element(new_e1))
        self.assertTrue(lww_set.lookup_element(self.e2))

        # resultant document should be
        # Add: {1:1112, 2:2222}
        self.assertEqual(str(lww_set.get_resultant_document()), '[1:1112, 2:2222]')

    def test_should_merge_two_lww_sets(self):
        """
        Test should merge two LWW-Element-Set properly
        """
        # person 1's lww set
        # Add: {1:1111, 2:2222}  Remove: {1:1111}
        lww1 = LWWElementSet()
        lww1.add(self.e1)
        lww1.add(self.e2)
        lww1.remove(self.e1)

        # person 2's lww set
        # Add: {1:1234, 2:2345, 3:3456}  Remove: {3:3456}
        lww2 = LWWElementSet()
        lww2.add(self.e10)
        lww2.add(self.e11)
        lww2.add(self.e12)
        lww2.remove(self.e12)

        merge_set = lww1 + lww2

        # only latest 2:timestamp should be added (2:2345 instead of 2:2222).
        self.assertEqual(str(merge_set.AddSet), '{1: 1234, 2: 2345, 3: 3456}')
        self.assertEqual(str(merge_set.RemoveSet), '{1: 1111, 3: 3456}')

        # resultant document structure, based on AddSet and RemoveSet
        final_document = merge_set.get_resultant_document()
        self.assertEqual(str(final_document), '[1:1234, 2:2345]')

    def test_should_generate_hi_world(self):
        """
        Test should generate correct resultant document
        """
        # person 1's lww set
        lww1 = LWWElementSet()
        hello = 'Hi'
        t = 0
        for s in hello:
            t = t + 1
            lww1.add(Element(s, t))

        # person 2's lww set
        lww2 = LWWElementSet()
        world = 'World'
        for s in world:
            t = t + 1
            lww2.add(Element(s, t))

        # person 3's lww set
        lww3 = LWWElementSet()
        hi_world = 'Hi, World!'
        for s in hi_world:
            t = t + 1
            lww3.add(Element(s, t))

        # merge 1 & 2 & 3
        merge_set = lww1 + lww2 + lww3
        # Resultant document should contain 'Hi, World!'
        self.assertEqual(str(merge_set.get_resultant_document()), '[H:8, i:9, W:12, o:13, r:14, l:15, d:16, ,:10,  :11, !:17]')

    def test_should_generate_correct_result_if_original_document_modified_in_parallel(self):
        """
        Test should generate correct resultant document if the original one updated in parallel
        """
        # original document
        lww = LWWElementSet()
        abc = "ABCDEFG"
        t = 0
        for s in abc:
            t = t + 1
            lww.add(Element(s, t))

        # person 1's updates
        lww1 = LWWElementSet()
        added = "HIJKL"
        removed = "ACEG"
        i = len(abc)
        for a in added:
            i = i + 1
            lww1.add(Element(a, t))

        for r in removed:
            i = i + 1
            lww1.remove(Element(r, t))

        # merge original and person 1's update
        result1 = lww + lww1
        # Original: ABCDEFG
        # Added: HIJKL  Removed: ACEG
        self.assertEqual(str(''.join([x.item for x in result1.get_resultant_document()])), 'BDFHIJKL')

        # person 2's parallel updates
        lww2 = LWWElementSet()
        added = "KLMNOP"
        removed = "BFG"
        i = len(abc) # to simulate parallel time, starting i with same as person 1's i
        for a in added:
            i = i + 1
            lww2.add(Element(a, t))

        for r in removed:
            i = i + 1
            lww2.remove(Element(r, t))

        # merge original and person 2's update
        result2 = lww + lww2
        # Original: ABCDEFG
        # Added: KLMNOP  Removed: BFG
        self.assertEqual(str(''.join([x.item for x in result2.get_resultant_document()])), 'ACDEKLMNOP')

        # final state of original document after, merge of both person's updates
        final = result1 + result2
        # Original: ABCDEFG
        # Person 1 : Added : HIJKL  Removed : ACEG
        # Person 2 : Added : KLMNOP Removed : BFG
        self.assertEqual(str(''.join([x.item for x in final.get_resultant_document()])), 'DHIJKLMNOP')







