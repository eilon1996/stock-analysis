def req1(n):
    if n <= -1:
        return
    print(n)
    req1(n - 1)


def req2(str):
    if len(str) <= 1:
        return str
    return str[-1] + req2(str[1:-1]) + str[0]


class TreeNode(object):
    def __init__(self, x):
        self.val = x
        self.left = None
        self.right = None

    def __str__(self):
        return str(self.val)


def tree_arange(lst):
    if len(lst) == 1:
        return TreeNode(lst[0])
    if len(lst) == 0:
        return None
    mid = len(lst) // 2
    root = TreeNode(lst[mid])
    root.left = tree_arange(lst[:mid])
    root.right = tree_arange(lst[mid + 1:])
    return root


def find_closest(root, k, closest=10 ** 8):
    if root == None:
        return closest
    if root.val == k:
        return k
    if root.val > k:
        if abs(closest - k) > abs(root.val - k):
            closest = root.val
        return find_closest(root.left, k, closest)
    if root.val < k:
        if abs(closest - k) > abs(root.val - k):
            closest = root.val
        return find_closest(root.right, k, closest)


print("root: " + str(tree_arange([1, 2, 3, 4, 5])) + ", closest: " + str(    find_closest(tree_arange([1, 2, 3, 4, 5]), 4)) + ", k= 4")
print(find_closest(tree_arange([1, 2, 3, 4, 5, 6, 7, 8]), 5.5))
print(find_closest(tree_arange([1, 2, 3, 4, 5, 6]), 4.1))
print(find_closest(tree_arange([1, 2, 3, 4, 5]), 8))
print(find_closest(tree_arange([1, 2, 3, 4, 5, 6, 7, 8]), -5))
print(find_closest(tree_arange([-3, -2, 3, 4, 5, 6]), 0))
