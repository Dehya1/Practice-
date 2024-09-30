# 当然，列表推导式（List
# Comprehension）是Python中一种非常强大且简洁的构建列表的方式。它允许你从一个已有的列表或迭代器中创建一个新的列表，同时可以对每个元素进行操作或满足特定条件时才包含该元素。
#
# 下面是一个简单的列表推导式例子，它创建了一个新列表，这个新列表包含了原列表中每个元素的平方：
#
# python
# 原列表  
numbers = [1, 2, 3, 4, 5]

# 使用列表推导式创建新列表，包含原列表中每个元素的平方  
squared_numbers = [x ** 2 for x in numbers]

print(squared_numbers)
# 输出: [1, 4, 9, 16, 25]
# 在这个例子中，for x in numbers部分遍历了numbers列表中的每个元素，而x ** 2则对每个元素进行了平方操作。整个表达式[x ** 2 for x in numbers]的结果是一个新列表，包含了原列表中每个元素平方后的值。
#
# 列表推导式还可以包含条件表达式，用于过滤掉不满足条件的元素。以下是一个包含条件表达式的列表推导式例子，它创建了一个新列表，这个新列表只包含了原列表中偶数元素的平方：

# python
# 原列表  
numbers = [1, 2, 3, 4, 5]

# 使用列表推导式创建新列表，包含原列表中偶数元素的平方  
squared_even_numbers = [x ** 2 for x in numbers if x % 2 == 0]  # for 循环遍历每一个number，把每一个数都平方，最后如果保留余数为0的，也就是保留整数组成一个列表

print(squared_even_numbers)
# 输出: [4, 16]
# 在这个例子中，if x % 2 == 0是一个条件表达式，它确保了只有当x是偶数时，x ** 2的结果才会被包含在新列表中。

print(len(range(5)))
a= [x for x in range(5)]
print(a)
a= [x+1 for x in range(5)]
print(a)
print('-'*80)
# 生成器表达式
gen_exp = (x**2 for x in range(5))
print(gen_exp)

