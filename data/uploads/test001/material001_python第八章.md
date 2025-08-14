# Python 第八章 函数

在本章中，你将学习编写**函数**（function）。函数是带名字的代码块，用于完成具体的工作。要执行函数定义的特定任务，可**调用**（call）该函数。当需要在程序中多次执行同一项任务时，无须反复编写完成该任务的代码，只需要调用执行该任务的函数，让 Python 运行其中的代码即可。你将发现，使用函数，程序编写、阅读、测试和修复起来都会更容易。

你还将学习各种向函数传递信息的方式，学习编写主要任务是显示信息的函数，以及用于处理数据并返回一个或一组值的函数。最后，你将学习如何将函数存储在称为**模块**（module）的独立文件中，让主程序文件更加整洁。

## 定义函数

下面是一个打印问候语的简单函数，名为 greet_user()：

### greeter.py 示例

```python
def greet_user():
    """ 显示简单的问候语 """
    print("Hello!")

greet_user()
```

#### 函数定义的基本结构

这个示例演示了最简单的函数结构。第一行代码使用关键字 def 来告诉 Python，你要定义一个函数。这是**函数定义**，向 Python 指出了函数名，还可以在括号内指出函数为完成任务需要什么样的信息。在这里，函数名为 greet_user()，它不需要任何信息就能完成工作，因此括号内是空的（即便如此，括号也必不可少）。最后，定义以冒号结尾。

#### 函数体和文档字符串

紧跟在 def greet_user():后面的所有缩进行构成了函数体。第二行的文本是称为**文档字符串**（docstring）的注释，描述了函数是做什么的。Python 在为程序中的函数生成文档时，会查找紧跟在函数定义后的字符串。这些字符串通常前后分别用三个双引号引起，能够包含多行。

代码行 print("Hello!")是函数体内的唯一行代码，因此 greet_user()只做一项工作：打印 Hello!。

#### 函数调用

要使用这个函数，必须调用它。**函数调用**让 Python 执行函数中的代码。要调用函数，可依次指定函数名以及用括号括起的必要信息。由于这个函数不需要任何信息，调用它时只需输入 greet_user()即可。和预期的一样，它会打印 Hello!：

```
Hello!
```

### 向函数传递信息

只需稍作修改，就可让 greet_user()函数在问候用户时以其名字作为抬头。为此，可在函数定义 def greet_user()的括号内添加 username。这样，可让函数接受你给 username 指定的任何值。现在，这个函数要求你在调用它时给 username 指定一个值。因此在调用 greet_user()时，可将一个名字传递给它，如下所示：

```python
def greet_user(username):
    """ 显示简单的问候语 """
    print(f"Hello, {username.title()}!")

greet_user('jesse')
```

#### 函数调用的结果

代码 greet_user('jesse')调用函数 greet_user()，并向它提供执行函数调用 print()所需的信息。这个函数接受你传递给它的名字，并向这个人发出问候：

```
Hello, Jesse!
```

同样，greet_user('sarah')调用函数 greet_user()并向它传递'sarah'，从而打印 Hello, Sarah!。你可以根据需要调用函数 greet_user()任意多次，无论在调用时传入什么名字，都将生成相应的输出。

### 实参和形参

前面在定义 greet_user()函数时，要求给变量 username 指定一个值。这样，在调用这个函数并提供这种信息（人名）时，它将打印相应的问候语。

#### 形参的概念

在 greet_user()函数的定义中，变量 username 是一个**形参**（parameter），即函数完成工作所需的信息。

#### 实参的概念

在代码 greet_user('jesse')中，值'jesse'是一个**实参**（argument），即在调用函数时传递给函数的信息。在调用函数时，我们将要让函数使用的信息放在括号内。在 greet_user('jesse')这个示例中，我们将实参'jesse'传递给函数 greet_user()，这个值被赋给了形参 username。

注意：大家有时候会形参、实参不分。即使你看到有人将函数定义中的变量称为实参或将函数调用中的变量称为形参，也不要大惊小怪。

## 传递实参

函数定义中可能包含多个形参，因此函数调用中也可能包含多个实参。向函数传递实参的方式很多：既可以使用**位置实参**，这要求实参的顺序与形参的顺序相同；也可以使用**关键字实参**，其中每个实参都由变量名和值组成；还可以使用列表和字典。下面依次介绍这些方式。

### 位置实参

在调用函数时，Python 必须将函数调用中的每个实参关联到函数定义中的一个形参。最简单的方式是基于实参的顺序进行关联。以这种方式关联的实参称为**位置实参**。

为了明白其中的工作原理，我们来看一个显示宠物信息的函数。这个函数指出一个宠物属于哪种动物以及它叫什么名字，如下所示：

#### pets.py 示例

```python
def describe_pet(animal_type, pet_name):
    """ 显示宠物的信息 """
    print(f"\nI have a {animal_type}.")
    print(f"My {animal_type}'s name is {pet_name.title()}.")

describe_pet('hamster', 'harry')
```

这个函数的定义表明，它需要一个动物类型和一个名字。在调用 describe_pet()时，需要按顺序提供一个动物类型和一个名字。例如，在刚才的函数调用中，实参'hamster'被赋给形参 animal_type，而实参'harry'被赋给形参 pet_name。在函数体内，使用这两个形参来显示宠物的信息。

输出描述了一只名为 Harry 的仓鼠：

```
I have a hamster.
My hamster's name is Harry.
```

#### 调用函数多次

可根据需要调用函数任意多次。要再描述一个宠物，只需再次调用 describe_pet()即可：

```python
def describe_pet(animal_type, pet_name):
    """ 显示宠物的信息 """
    print(f"\nI have a {animal_type}.")
    print(f"My {animal_type}'s name is {pet_name.title()}.")

describe_pet('hamster', 'harry')
describe_pet('dog', 'willie')
```

第二次调用 describe_pet()函数时，向它传递实参'dog'和'willie'。与第一次调用时一样，Python 将实参'dog'关联到形参 animal_type，并将实参'willie'关联到形参 pet_name。

与前面一样，这个函数完成了任务，但打印的是一条名为 Willie 的小狗的信息。至此，有一只名为 Harry 的仓鼠，还有一条名为 Willie 的小狗：

```
I have a hamster.
My hamster's name is Harry.

I have a dog.
My dog's name is Willie.
```

多次调用同一个函数是一种效率极高的工作方式。只需在函数中编写一次描述宠物的代码，每当需要描述新宠物时，就都可以调用这个函数并向它提供新宠物的信息。即便描述宠物的代码增加到了 10 行，依然只需使用一行调用函数的代码，就可以描述一个新宠物。

在函数中，可根据需要使用任意数量的位置实参，Python 将按顺序将函数调用中的实参关联到函数定义中相应的形参。

#### 位置实参的顺序很重要

当使用位置实参来调用函数时，如果实参的顺序不正确，结果可能会出乎意料：

```python
def describe_pet(animal_type, pet_name):
    """ 显示宠物的信息 """
    print(f"\nI have a {animal_type}.")
    print(f"My {animal_type}'s name is {pet_name.title()}.")

describe_pet('harry', 'hamster')
```

在这个函数调用中，先指定名字，再指定动物类型。由于实参'harry'在前，这个值将被赋给形参 animal_type，而后面的'hamster'将被赋给形参 pet_name。结果是有一个名为 Hamster 的 harry：

```
I have a harry.
My harry's name is Hamster.
```

如果你得到的结果像上面一样可笑，请确认函数调用中实参的顺序与函数定义中形参的顺序是否一致。

### 关键字实参

**关键字实参**是传递给函数的名值对。这样会直接在实参中将名称和值关联起来，因此向函数传递实参时就不会混淆了（不会得到名为 Hamster 的 harry 这样的结果）。关键字实参不仅让你无须考虑函数调用中的实参顺序，而且清楚地指出了函数调用中各个值的用途。

下面重新编写 pets.py，在其中使用关键字实参来调用 describe_pet()：

```python
def describe_pet(animal_type, pet_name):
    """ 显示宠物的信息 """
    print(f"\nI have a {animal_type}.")
    print(f"My {animal_type}'s name is {pet_name.title()}.")

describe_pet(animal_type='hamster', pet_name='harry')
```

#### 关键字实参的优势

describe_pet()函数还和之前一样，但这次调用这个函数时，向 Python 明确地指出了各个实参对应的形参。当看到这个函数调用时，Python 知道应该将实参'hamster'和'harry'分别赋给形参 animal_type 和 pet_name。输出正确无误，指出有一只名为 Harry 的仓鼠。

关键字实参的顺序无关紧要，因为 Python 知道各个值该被赋给哪个形参。下面两个函数调用是等效的：

```python
describe_pet(animal_type='hamster', pet_name='harry')
describe_pet(pet_name='harry', animal_type='hamster')
```

注意：在使用关键字实参时，务必准确地指定函数定义中的形参名。

### 默认值

在编写函数时，可以给每个形参指定**默认值**。如果在调用函数中给形参提供了实参，Python 将使用指定的实参值；否则，将使用形参的默认值。因此，给形参指定默认值后，可在函数调用中省略相应的实参。使用默认值不仅能简化函数调用，还能清楚地指出函数的典型用法。

如果你发现在调用 describe_pet()时，描述的大多是小狗，就可将形参 animal_type 的默认值设置为'dog'。这样，当调用 describe_pet()来描述小狗时，就可以不提供该信息：

```python
def describe_pet(pet_name, animal_type='dog'):
    """ 显示宠物的信息 """
    print(f"\nI have a {animal_type}.")
    print(f"My {animal_type}'s name is {pet_name.title()}.")

describe_pet(pet_name='willie')
```

#### 默认值的使用规则

这里修改了 describe_pet()函数的定义，在其中给形参 animal_type 指定了默认值'dog'。这样，在调用这个函数时，如果没有给 animal_type 指定值，Python 将自动把这个形参设置为'dog'：

```
I have a dog.
My dog's name is Willie.
```

请注意，在这个函数的定义中，修改了形参的排列顺序。由于给 animal_type 指定了默认值，无须通过实参来指定动物类型，因此函数调用只包含一个实参——宠物的名字。然而，Python 依然将这个实参视为位置实参，如果函数调用只包含宠物的名字，这个实参将被关联到函数定义中的第一个形参。这就是需要将 pet_name 放在形参列表开头的原因。

现在，使用这个函数的最简单方式是，在函数调用中只提供小狗的名字：

```python
describe_pet('willie')
```

这个函数调用的输出与前一个示例相同。只提供了一个实参'willie'，这个实参将被关联到函数定义中的第一个形参 pet_name。由于没有给 animal_type 提供实参，因此 Python 使用默认值'dog'。

如果要描述的动物不是小狗，可使用类似于下面的函数调用：

```python
describe_pet(pet_name='harry', animal_type='hamster')
```

由于显式地给 animal_type 提供了实参，Python 将忽略这个形参的默认值。

注意：当使用默认值时，必须在形参列表中先列出没有默认值的形参，再列出有默认值的形参。这让 Python 依然能够正确地解读位置实参。

### 等效的函数调用

鉴于可混合使用位置实参、关键字实参和默认值，通常有多种等效的函数调用方式。请看 describe_pet()函数的如下定义，其中给一个形参提供了默认值：

```python
def describe_pet(pet_name, animal_type='dog'):
```

基于这种定义，在任何情况下都必须给 pet_name 提供实参。在指定该实参时，既可以使用位置实参，也可以使用关键字实参。如果要描述的动物不是小狗，还必须在函数调用中给 animal_type 提供实参。同样，在指定该实参时，既可以使用位置实参，也可以使用关键字实参。

下面对这个函数的所有调用都可行：

```python
# 一条名为Willie的小狗
describe_pet('willie')
describe_pet(pet_name='willie')

# 一只名为Harry的仓鼠
describe_pet('harry', 'hamster')
describe_pet(pet_name='harry', animal_type='hamster')
describe_pet(animal_type='hamster', pet_name='harry')
```

这些函数调用的输出与前面的示例相同。

使用哪种调用方式无关紧要。可以使用对你来说最容易理解的调用方式，只要函数调用能生成你期望的输出就好。

### 避免实参错误

等你开始使用函数后，也许会遇到实参不匹配错误。当你提供的实参多于或少于函数完成工作所需的实参数量时，将出现实参不匹配错误。如果在调用 describe_pet()函数时没有指定任何实参，结果将如何呢？

```python
def describe_pet(animal_type, pet_name):
    """ 显示宠物的信息 """
    print(f"\nI have a {animal_type}.")
    print(f"My {animal_type}'s name is {pet_name.title()}.")

describe_pet()
```

#### 错误信息的解读

Python 发现该函数调用缺少必要的信息，并用 traceback 指出了这一点：

```
Traceback (most recent call last):
  File "pets.py", line 6, in <module>
    describe_pet()
    ^^^^^^^^^^^^^^
TypeError: describe_pet() missing 2 required positional arguments: 'animal_type' and 'pet_name'
```

traceback 首先指出问题出在什么地方，让我们能够回过头去找出函数调用中的错误。然后，指出导致问题的函数调用。最后，traceback 指出该函数调用缺少两个实参，并指出了相应形参的名称。如果这个函数存储在一个独立的文件中，我们也许无须打开这个文件并查看函数的代码，就能重新正确地编写函数调用。

Python 能读取函数的代码，并指出需要为哪些形参提供实参，这为我们提供了极大的帮助。这是应该给变量和函数指定描述性名称的另一个原因：如果这样做了，那么无论对于你，还是可能使用你编写的代码的其他任何人来说，Python 提供的错误消息都将更有帮助性。

如果提供的实参太多，将出现类似的 traceback，帮助你确保函数调用和函数定义匹配。

## 返回值

函数并非总是直接显示输出，它还可以处理一些数据，并返回一个或一组值。函数返回的值称为**返回值**。在函数中，可以使用 return 语句将值返回到调用函数的那行代码。返回值让你能够将程序的大部分繁重工作移到函数中完成，从而简化主程序。

### 返回简单的值

下面来看一个函数，它接受名和姓并返回标准格式的姓名：

#### formatted_name.py 示例

```python
def get_formatted_name(first_name, last_name):
    """ 返回标准格式的姓名 """
    full_name = f"{first_name} {last_name}"
    return full_name.title()

musician = get_formatted_name('jimi', 'hendrix')
print(musician)
```

get_formatted_name()函数的定义通过形参接受名和姓。它将名和姓合在一起，在中间加上一个空格，并将结果赋给变量 full_name。然后，它将 full_name 的值转换为首字母大写的格式，并将结果返回函数调用行。

在调用可以返回值的函数时，需要提供一个变量，以便将返回的值赋给它。这里将返回值赋给了变量 musician。输出为标准格式的姓名：

```
Jimi Hendrix
```

原本只需编写下面的代码就可以输出这个标准格式的姓名，前面做的工作好像太多了：

```python
print("Jimi Hendrix")
```

你要知道，在需要分别存储大量名和姓的大型程序中，像 get_formatted_name()这样的函数非常有用。你可以分别存储名和姓，每当需要显示姓名时就调用这个函数。

### 让实参变成可选的

有时候，需要让实参变成可选的，以便使用函数的人只在必要时才提供额外的信息。可以使用默认值来让实参变成可选的。

假设要扩展 get_formatted_name()函数，使其除了名和姓之外还可以处理中间名。为此，可将其修改成类似这样：

```python
def get_formatted_name(first_name, middle_name, last_name):
    """ 返回标准格式的姓名 """
    full_name = f"{first_name} {middle_name} {last_name}"
    return full_name.title()

musician = get_formatted_name('john', 'lee', 'hooker')
print(musician)
```

只要同时提供名、中间名和姓，这个函数就能正确运行。它根据这三部分创建一个字符串，在适当的地方加上空格，并将结果转换为首字母大写的格式：

```
John Lee Hooker
```

#### 处理可选的中间名

然而，并非所有人都有中间名。如果调用这个函数时只提供了名和姓，它将不能正确地运行。为让中间名变成可选的，可给形参 middle_name 指定默认值（空字符串），在用户不提供中间名时不使用这个形参。为了让 get_formatted_name()在没有提供中间名时依然正确运行，可给形参 middle_name 指定默认值（空字符串），并将其移到形参列表的末尾：

```python
def get_formatted_name(first_name, last_name, middle_name=''):
    """ 返回标准格式的姓名 """
    if middle_name:
        full_name = f"{first_name} {middle_name} {last_name}"
    else:
        full_name = f"{first_name} {last_name}"
    return full_name.title()

musician = get_formatted_name('jimi', 'hendrix')
print(musician)

musician = get_formatted_name('john', 'hooker', 'lee')
print(musician)
```

在这个示例中，姓名是根据三个可能提供的部分创建的。每个人都有名和姓，因此在函数定义中首先列出了这两个形参。中间名是可选的，因此在函数定义中最后列出该形参，并将其默认值设置为空字符串。

在函数体中，检查是否提供了中间名。Python 将非空字符串解读为 True，如果在函数调用中提供了中间名，条件测试 if middle_name 将为 True。如果提供了中间名，就将名、中间名和姓合并为姓名，再将其修改为首字母大写的格式，并将结果返回函数调用行。在函数调用行，将返回的值赋给变量 musician。最后，这个变量的值被打印了出来。如果没有提供中间名，middle_name 将为空字符串，导致 if 测试未通过，进而执行 else 代码块：只使用名和姓来生成姓名，并将设置好格式的姓名返回函数调用行。在函数调用行，将返回的值赋给变量 musician。最后，这个变量的值被打印了出来。

在调用这个函数时，如果只想指定名和姓，调用起来将非常简单。如果还要指定中间名，就必须确保它是最后一个实参，这样 Python 才能正确地将位置实参关联到形参。

这个修改后的版本不仅适用于只有名和姓的人，也适用于还有中间名的人：

```
Jimi Hendrix
John Lee Hooker
```

可选值在让函数能够处理各种不同情形的同时，确保函数调用尽可能简单。

### 返回字典

函数可返回任何类型的值，包括列表和字典等较为复杂的数据结构。例如，下面的函数接受姓名的组成部分，并返回一个表示人的字典：

#### person.py 示例

```python
def build_person(first_name, last_name):
    """ 返回一个字典，其中包含有关一个人的信息 """
    person = {'first': first_name, 'last': last_name}
    return person

musician = build_person('jimi', 'hendrix')
print(musician)
```

build_person()函数接受名和姓，并将这些值放在字典中。在存储 first_name 的值时，使用的键为'first'，而在存储 last_name 的值时，使用的键为'last'。然后，返回表示人的整个字典。在此处，打印这个被返回的值。此时，原来的两项文本信息存储在一个字典中：

```
{'first': 'jimi', 'last': 'hendrix'}
```

#### 扩展字典功能

这个函数接受简单的文本信息，并将其放在一个更合适的数据结构中，让你不仅能打印这些信息，还能以其他方式处理它们。当前，字符串'jimi'和'hendrix'分别被标记为名和姓。你可以轻松地扩展这个函数，使其接受可选值，如中间名、年龄、职业或其他任何要存储的信息。例如，下面的修改能让你存储年龄：

```python
def build_person(first_name, last_name, age=None):
    """ 返回一个字典，其中包含有关一个人的信息 """
    person = {'first': first_name, 'last': last_name}
    if age:
        person['age'] = age
    return person
```

在函数定义中，新增了一个可选形参 age，其默认值被设置为特殊值 None（表示变量没有值）。可将 None 视为占位值。在条件测试中，None 相当于 False。如果函数调用中包含形参 age 的值，这个值将被存储到字典中。在任何情况下，这个函数都会存储一个人的姓名，并且可以修改它，使其同时存储有关这个人的其他信息。

### 结合使用函数和 while 循环

可将函数与本书前面介绍的所有 Python 结构结合起来使用。例如，下面将结合使用 get_formatted_name()函数和 while 循环，以更正规的方式问候用户。下面尝试使用名和姓跟用户打招呼：

#### greeter.py 示例

```python
def get_formatted_name(first_name, last_name):
    """ 返回规范格式的姓名 """
    full_name = f"{first_name} {last_name}"
    return full_name.title()

# 这是一个无限循环!
while True:
    print("\nPlease tell me your name:")
    f_name = input("First name: ")
    l_name = input("Last name: ")

    formatted_name = get_formatted_name(f_name, l_name)
    print(f"\nHello, {formatted_name}!")
```

在这个示例中，使用的是 get_formatted_name()的简单版本，不涉及中间名。while 循环让用户输入姓名：提示用户依次输入名和姓。

#### 提供退出条件

但这个 while 循环存在一个问题：没有定义退出条件。在请用户进行一系列输入时，该在什么地方提供退出途径呢？我们要让用户能够尽可能容易地退出，因此在每次提示用户输入时，都应提供退出途径。使用 break 语句可以在每次提示用户输入时提供退出循环的简单途径：

```python
def get_formatted_name(first_name, last_name):
    """ 返回规范格式的姓名 """
    full_name = f"{first_name} {last_name}"
    return full_name.title()

while True:
    print("\nPlease tell me your name:")
    print("(enter 'q' at any time to quit)")

    f_name = input("First name: ")
    if f_name == 'q':
        break

    l_name = input("Last name: ")
    if l_name == 'q':
        break

    formatted_name = get_formatted_name(f_name, l_name)
    print(f"\nHello, {formatted_name}!")
```

我们添加了一条消息来告诉用户如何退出。然后在每次提示用户输入时，都检查他输入的是否是退出值。如果是，就退出循环。现在，这个程序将不断地发出问候，直到用户输入的姓或名为'q'：

```
Please tell me your name:
(enter 'q' at any time to quit)
First name: eric
Last name: matthes

Hello, Eric Matthes!

Please tell me your name:
(enter 'q' at any time to quit)
First name: q
```

## 传递列表

你经常会发现，向函数传递列表很有用，可能是名字列表、数值列表或更复杂的对象列表（如字典）。将列表传递给函数后，函数就能直接访问其内容。下面使用函数来提高处理列表的效率。

假设有一个用户列表，而我们要向其中的每个用户发出问候。下面的示例将一个名字列表传递给一个名为 greet_users()的函数，这个函数会向列表中的每个人发出问候：

#### greet_users.py 示例

```python
def greet_users(names):
    """ 向列表中的每个用户发出简单的问候 """
    for name in names:
        msg = f"Hello, {name.title()}!"
        print(msg)

usernames = ['hannah', 'ty', 'margot']
greet_users(usernames)
```

我们将 greet_users()定义成接受一个名字列表，并将其赋给形参 names。这个函数遍历收到的列表，并对其中的每个用户打印一条问候语。在函数外，先定义一个用户列表 usernames，再调用 greet_users()并将这个列表传递给它：

```
Hello, Hannah!
Hello, Ty!
Hello, Margot!
```

输出完全符合预期。每个用户都看到了一条个性化的问候语。每当需要问候一组用户时，都可调用这个函数。

### 在函数中修改列表

将列表传递给函数后，函数就可以对其进行修改了。在函数中对这个列表所做的任何修改都是永久的，这让你能够高效地处理大量数据。

来看一家为用户提交的设计制作 3D 打印模型的公司。需要打印的设计事先存储在一个列表中，打印后将被移到另一个列表中。下面是在不使用函数的情况下模拟这个过程的代码：

#### printing_models.py 示例

```python
# 首先创建一个列表，其中包含一些要打印的设计
unprinted_designs = ['phone case', 'robot pendant', 'dodecahedron']
completed_models = []

# 模拟打印每个设计，直到没有未打印的设计为止
# 打印每个设计后，都将其移到列表completed_models中
while unprinted_designs:
    current_design = unprinted_designs.pop()
    print(f"Printing model: {current_design}")
    completed_models.append(current_design)

# 显示打印好的所有模型
print("\nThe following models have been printed:")
for completed_model in completed_models:
    print(completed_model)
```

这个程序首先创建一个需要打印的设计列表，以及一个名为 completed_models 的空列表，打印每个设计后都将其移到这个空列表中。只要列表 unprinted_designs 中还有设计，while 循环就模拟打印设计的过程：从该列表末尾删除一个设计，将其赋给变量 current_design，并显示一条消息，指出正在打印当前的设计，再将该设计加入列表 completed_models。循环结束后，显示已打印的所有设计：

```
Printing model: dodecahedron
Printing model: robot pendant
Printing model: phone case

The following models have been printed:
dodecahedron
robot pendant
phone case
```

#### 使用函数重新组织代码

可以重新组织这些代码，编写两个函数，让每个都做一件具体的工作。大部分代码与原来相同，只是结构更为合理。第一个函数负责处理打印设计的工作，第二个概述打印了哪些设计：

```python
def print_models(unprinted_designs, completed_models):
    """
    模拟打印每个设计，直到没有未打印的设计为止
    打印每个设计后，都将其移到列表completed_models中
    """
    while unprinted_designs:
        current_design = unprinted_designs.pop()
        print(f"Printing model: {current_design}")
        completed_models.append(current_design)

def show_completed_models(completed_models):
    """ 显示打印好的所有模型 """
    print("\nThe following models have been printed:")
    for completed_model in completed_models:
        print(completed_model)

unprinted_designs = ['phone case', 'robot pendant', 'dodecahedron']
completed_models = []

print_models(unprinted_designs, completed_models)
show_completed_models(completed_models)
```

首先，定义函数 print_models()，它包含两个形参：一个需要打印的设计列表和一个打印好的模型列表。给定这两个列表，这个函数模拟打印每个设计的过程：将设计逐个从未打印的设计列表中取出，并加入打印好的模型列表。然后，定义函数 show_completed_models()，它包含一个形参：打印好的模型列表。给定这个列表，函数 show_completed_models()显示打印出来的每个模型的名称。

虽然这个程序的输出与未使用函数的版本相同，但是代码更有条理。完成大部分工作的代码被移到了两个函数中，让主程序很容易理解。只要看看主程序，你就能轻松地知道这个程序的功能：

```python
unprinted_designs = ['phone case', 'robot pendant', 'dodecahedron']
completed_models = []

print_models(unprinted_designs, completed_models)
show_completed_models(completed_models)
```

我们创建了一个未打印的设计列表，以及一个空列表，后者用于存储打印好的模型。接下来，由于已经定义了两个函数，因此只需要调用它们并传入正确的实参即可。我们调用 print_models()并向它传递两个列表。像预期的一样，print_models()模拟了打印设计的过程。接下来，调用 show_completed_models()，并将打印好的模型列表传递给它，让它能够指出打印了哪些模型。描述性的函数名让阅读这些代码的人也能一目了然，虽然其中没有任何注释。

相比于没有使用函数的版本，这个程序更容易扩展和维护。如果以后需要打印其他设计，只需再次调用 print_models()即可。如果发现需要对模拟打印的代码进行修改，只需修改这些代码一次，就将影响所有调用该函数的地方。与必须分别修改程序的多个地方相比，这种修改的效率更高。

这个程序还演示了一种理念：每个函数都应只负责一项具体工作。用第一个函数打印每个设计，用第二个函数显示打印好的模型，优于使用一个函数完成这两项工作。在编写函数时，如果发现它执行的任务太多，请尝试将这些代码划分到两个函数中。别忘了，总是可以在一个函数中调用另一个函数，这有助于将复杂的任务分解成一系列步骤。

### 禁止函数修改列表

有时候，需要禁止函数修改列表。假设像前一个示例那样，你有一个未打印的设计列表，并且编写了一个将这些设计移到打印好的模型列表中的函数。你可能会做出这样的决定：即便打印了所有的设计，也要保留原来的未打印的设计列表，作为存档。但由于你将所有的设计都移出了 unprinted_designs，这个列表变成了空的——原来的列表没有了。为了解决这个问题，可向函数传递列表的副本而不是原始列表。这样，函数所做的任何修改都只影响副本，而丝毫不影响原始列表。

#### 传递列表副本的方法

要将列表的副本传递给函数，可以像下面这样做：

```python
function_name(list_name[:])
```

切片表示法[:]创建列表的副本。在 printing_models.py 中，如果不想清空未打印的设计列表，可像下面这样调用 print_models()：

```python
print_models(unprinted_designs[:], completed_models)
```

print_models()函数依然能够完成其工作，因为它获得了所有未打印的设计的名称，但它这次使用的是列表 unprinted_designs 的副本，而不是列表 unprinted_designs 本身。像以前一样，列表 completed_models 将包含打印好的模型的名称，但函数所做的修改不会影响列表 unprinted_designs。

虽然向函数传递列表的副本可保留原始列表的内容，但除非有充分的理由，否则还是应该将原始列表传递给函数。这是因为，让函数使用现成的列表可避免花时间和内存创建副本，从而提高效率，在处理大型列表时尤其如此。

## 传递任意数量的实参

有时候，你预先不知道函数需要接受多少个实参，好在 Python 允许函数从调用语句中收集任意数量的实参。

例如一个制作比萨的函数，它需要接受很多配料，但无法预先确定顾客要点多少种配料。下面的函数只有一个形参\*toppings，不管调用语句提供了多少实参，这个形参都会将其收入囊中：

#### pizza.py 示例

```python
def make_pizza(*toppings):
    """ 打印顾客点的所有配料 """
    print(toppings)

make_pizza('pepperoni')
make_pizza('mushrooms', 'green peppers', 'extra cheese')
```

形参名\*toppings 中的星号让 Python 创建一个名为 toppings 的元组，该元组包含函数收到的所有值。函数体内的函数调用 print()生成的输出证明，Python 既能处理使用一个值调用函数的情形，也能处理使用三个值调用函数的情形。它以类似的方式处理不同的调用。注意，Python 会将实参封装到一个元组中，即便函数只收到一个值也是如此：

```
('pepperoni',)
('mushrooms', 'green peppers', 'extra cheese')
```

现在，可以将函数调用 print()替换为一个循环，遍历配料列表并对顾客点的比萨进行描述：

```python
def make_pizza(*toppings):
    """ 概述要制作的比萨 """
    print("\nMaking a pizza with the following toppings:")
    for topping in toppings:
        print(f"- {topping}")

make_pizza('pepperoni')
make_pizza('mushrooms', 'green peppers', 'extra cheese')
```

不管收到一个值还是三个值，这个函数都能妥善地处理：

```
Making a pizza with the following toppings:
- pepperoni

Making a pizza with the following toppings:
- mushrooms
- green peppers
- extra cheese
```

不管函数收到多少个实参，这种语法都管用。

### 结合使用位置实参和任意数量的实参

如果要让函数接受不同类型的实参，必须在函数定义中将接纳任意数量实参的形参放在最后。Python 先匹配位置实参和关键字实参，再将余下的实参都收集到最后一个形参中。

例如，如果前面的函数还需要一个表示比萨尺寸的形参，必须将该形参放在形参\*toppings 的前面：

```python
def make_pizza(size, *toppings):
    """ 概述要制作的比萨 """
    print(f"\nMaking a {size}-inch pizza with the following toppings:")
    for topping in toppings:
        print(f"- {topping}")

make_pizza(16, 'pepperoni')
make_pizza(12, 'mushrooms', 'green peppers', 'extra cheese')
```

基于上述函数定义，Python 将收到的第一个值赋给形参 size，将其他所有的值都存储在元组 toppings 中。在函数调用中，首先指定表示比萨尺寸的实参，再根据需要指定任意数量的配料。

现在，每个比萨都有了尺寸和一系列配料，而且这些信息被按正确的顺序打印出来了——首先是尺寸，然后是配料：

```
Making a 16-inch pizza with the following toppings:
- pepperoni

Making a 12-inch pizza with the following toppings:
- mushrooms
- green peppers
- extra cheese
```

注意：你经常会看到通用形参名\*args，它也这样收集任意数量的位置实参。

### 使用任意数量的关键字实参

有时候，你需要接受任意数量的实参，但预先不知道传递给函数的会是什么样的信息。在这种情况下，可将函数编写成能够接受任意数量的键值对——调用语句提供了多少就接受多少。一个这样的示例是创建用户简介：你知道将收到有关用户的信息，但不确定是什么样的信息。在下面的示例中，build_profile()函数不仅接受名和姓，还接受任意数量的关键字实参：

#### user_profile.py 示例

```python
def build_profile(first, last, **user_info):
    """ 创建一个字典，其中包含我们知道的有关用户的一切 """
    user_info['first_name'] = first
    user_info['last_name'] = last
    return user_info

user_profile = build_profile('albert', 'einstein',
                           location='princeton',
                           field='physics')
print(user_profile)
```

build_profile()函数的定义要求提供名和姓，同时允许根据需要提供任意数量的名值对。形参\*\*user_info 中的两个星号让 Python 创建一个名为 user_info 的字典，该字典包含函数收到的其他所有名值对。在这个函数中，可以像访问其他字典那样访问 user_info 中的名值对。

在 build_profile()的函数体内，将名和姓加入字典 user_info，因为总是会从用户那里收到这两项信息，而这两项信息还没被放在字典中。接下来，将字典 user_info 返回函数调用行。

我们调用 build_profile()，向它传递名（'albert'）、姓（'einstein'）和两个键值对（location='princeton'和 field='physics'），并将返回的 user_info 赋给变量 user_profile，再打印这个变量：

```
{'location': 'princeton', 'field': 'physics', 'first_name': 'albert', 'last_name': 'einstein'}
```

在这里，返回的字典包含用户的名和姓，还有居住地和研究领域。在调用这个函数时，不管额外提供多少个键值对，它都能正确地处理。

在编写函数时，可以用各种方式混合使用位置实参、关键字实参和任意数量的实参。知道这些实参类型大有裨益，因为你在阅读别人编写的代码时经常会见到它们。要正确地使用这些类型的实参并知道使用它们的时机，需要一定的练习。就目前而言，牢记使用最简单的方法来完成任务就好了。继续往下阅读，你就会知道在各种情况下使用哪种方法的效率最高。

注意：你经常会看到形参名\*\*kwargs，它用于收集任意数量的关键字实参。

## 将函数存储在模块中

使用函数的优点之一是可将代码块与主程序分离。通过给函数指定描述性名称，能让程序容易理解得多。你还可以更进一步，将函数存储在称为**模块**的独立文件中，再将模块导入（import）主程序。import 语句可让你在当前运行的程序文件中使用模块中的代码。

通过将函数存储在独立的文件中，可隐藏程序代码的细节，将重点放在程序的高层逻辑上。这还能让你在众多不同的程序中复用函数。将函数存储在独立文件中后，可与其他程序员共享这些文件而不是整个程序。知道如何导入函数还能让你使用其他程序员编写的函数库。

导入模块的方法有好几种，下面对每种都做简要的介绍。

### 导入整个模块

要让函数是可导入的，得先创建模块。**模块**是扩展名为.py 的文件，包含要导入程序的代码。下面来创建一个包含 make_pizza()函数的模块。为此，将文件 pizza.py 中除了函数 make_pizza()之外的代码删除：

#### pizza.py 模块

```python
def make_pizza(size, *toppings):
    """ 概述要制作的比萨 """
    print(f"\nMaking a {size}-inch pizza with the following toppings:")
    for topping in toppings:
        print(f"- {topping}")
```

接下来，在 pizza.py 所在的目录中创建一个名为 making_pizzas.py 的文件。这个文件先导入刚创建的模块，再调用 make_pizza()两次：

#### making_pizzas.py 示例

```python
import pizza

pizza.make_pizza(16, 'pepperoni')
pizza.make_pizza(12, 'mushrooms', 'green peppers', 'extra cheese')
```

当 Python 读取这个文件时，代码行 import pizza 会让 Python 打开文件 pizza.py，并将其中的所有函数都复制到这个程序中。你看不到复制代码的过程，因为 Python 会在程序即将运行时在幕后复制这些代码。你只需要知道，在 making_pizzas.py 中，可使用 pizza.py 中定义的所有函数。

要调用被导入模块中的函数，可指定被导入模块的名称 pizza 和函数名 make_pizza()，并用句点隔开。这些代码的输出与没有导入模块的原始程序相同：

```
Making a 16-inch pizza with the following toppings:
- pepperoni

Making a 12-inch pizza with the following toppings:
- mushrooms
- green peppers
- extra cheese
```

这就是一种导入方法：只需编写一条 import 语句并在其中指定模块名，就可在程序中使用该模块中的所有函数。如果使用这种 import 语句导入了名为 module_name.py 的整个模块，就可使用下面的语法来使用其中的任意一个函数：

```python
module_name.function_name()
```

### 导入特定的函数

还可以只导入模块中的特定函数，语法如下：

```python
from module_name import function_name
```

用逗号分隔函数名，可根据需要从模块中导入任意数量的函数：

```python
from module_name import function_0, function_1, function_2
```

对于前面的 making_pizzas.py 示例，如果只想导入要使用的函数，代码将类似于下面这样：

```python
from pizza import make_pizza

make_pizza(16, 'pepperoni')
make_pizza(12, 'mushrooms', 'green peppers', 'extra cheese')
```

如果使用这种语法，在调用函数时则无须使用句点。由于在 import 语句中显式地导入了 make_pizza()函数，因此在调用时只需指定其名称即可。

### 使用 as 给函数指定别名

如果要导入的函数的名称太长或者可能与程序中既有的名称冲突，可指定简短而独一无二的**别名**（alias）：函数的另一个名称，类似于外号。要给函数指定这种特殊的外号，需要在导入时这样做。

下面给 make_pizza()函数指定了别名 mp()。这是在 import 语句中使用 make_pizza as mp 实现的，关键字 as 将函数重命名为指定的别名：

```python
from pizza import make_pizza as mp

mp(16, 'pepperoni')
mp(12, 'mushrooms', 'green peppers', 'extra cheese')
```

上面的 import 语句将函数 make_pizza()重命名为 mp()。在这个程序中，每当需要调用 make_pizza()时，都可将其简写成 mp()。Python 将运行 make_pizza()中的代码，同时避免与程序可能包含的 make_pizza()函数混淆。

指定别名的通用语法如下：

```python
from module_name import function_name as fn
```

### 使用 as 给模块指定别名

还可以给模块指定别名。通过给模块指定简短的别名（如给 pizza 模块指定别名 p），你能够更轻松地调用模块中的函数。相比于 pizza.make_pizza()，p.make_pizza()显然更加简洁：

```python
import pizza as p

p.make_pizza(16, 'pepperoni')
p.make_pizza(12, 'mushrooms', 'green peppers', 'extra cheese')
```

上述 import 语句给 pizza 模块指定了别名 p，但该模块中所有函数的名称都没变。要调用 make_pizza()函数，可将其写为 p.make_pizza()而不是 pizza.make_pizza()。这样不仅让代码更加简洁，还让你不用再关注模块名，只专注于描述性的函数名。这些函数名明确地指出了函数的功能，对于理解代码来说，它们比模块名更重要。

给模块指定别名的通用语法如下：

```python
import module_name as mn
```

### 导入模块中的所有函数

使用星号（\*）运算符可让 Python 导入模块中的所有函数：

```python
from pizza import *

make_pizza(16, 'pepperoni')
make_pizza(12, 'mushrooms', 'green peppers', 'extra cheese')
```

import 语句中的星号让 Python 将模块 pizza 中的每个函数都复制到这个程序文件中。由于导入了每个函数，可通过名称来调用每个函数，无须使用**点号**（dot notation）。然而，在使用并非自己编写的大型模块时，最好不要使用这种导入方法，因为如果模块中有函数的名称与当前项目中既有的名称相同，可能导致意想不到的结果：Python 可能会因为遇到多个名称相同的函数或变量而覆盖函数，而不是分别导入所有的函数。

最佳的做法是，要么只导入需要使用的函数，要么导入整个模块并使用点号。这都能让代码更清晰，更容易阅读和理解。这里之所以介绍导入模块中所有函数的方法，只是想让你在阅读别人编写的代码时，能够理解类似于下面的 import 语句：

```python
from module_name import *
```

## 函数编写指南

在编写函数时，需要牢记几个细节。应给函数指定描述性名称，且只使用小写字母和下划线。描述性名称可帮助你和别人明白代码想要做什么。在给模块命名时也应遵循上述约定。

每个函数都应包含简要阐述其功能的注释。该注释应紧跟在函数定义后面，并采用文档字符串的格式。这样，其他程序员只需阅读文档字符串中的描述就能够使用它：他们完全可以相信代码会如描述的那样运行，并且只要知道函数名、需要的实参以及返回值的类型，就能在自己的程序中使用它。

### 格式规范

在给形参指定默认值时，等号两边不要有空格：

```python
def function_name(parameter_0, parameter_1='default value')
```

函数调用中的关键字实参也应遵循这种约定：

```python
function_name(value_0, parameter_1='value')
```

PEP 8 建议代码行的长度不要超过 79 个字符。这样，只要编辑器窗口适中，就能看到整行代码。如果形参很多，导致函数定义的长度超过了 79 个字符，可在函数定义中输入左括号后按回车键，并在下一行连按两次制表符键，从而将形参列表和只缩进一层的函数体区分开来。

大多数编辑器会自动对齐后续参数列表行，使其缩进程度与你给第一个参数列表行指定的缩进程度相同：

```python
def function_name(
        parameter_0, parameter_1, parameter_2,
        parameter_3, parameter_4, parameter_5):
    function body...
```

如果程序或模块包含多个函数，可使用两个空行将相邻的函数分开。这样将更容易知道前一个函数到什么地方结束，下一个函数从什么地方开始。

所有的 import 语句都应放在文件开头。唯一的例外是，你要在文件开头使用注释来描述整个程序。

## 小结

在本章中，你首先学习了如何编写函数，以及如何传递实参，让函数能够访问完成工作所需的信息。然后学习了如何使用位置实参和关键字实参，以及如何接受任意数量的实参。你见识了显示输出的函数和返回值的函数，知道了如何将函数与列表、字典、if 语句和 while 循环结合起来使用，以及如何将函数存储在称为模块的独立文件中，让程序文件更简单、更易于理解。最后，你了解了函数编写指南，遵循这些指南可让程序始终保持良好的结构，对你和其他人来说都易于阅读。

程序员的目标之一是编写简单的代码来完成任务，而函数有助于实现这样的目标。使用它们，你在编写好一个个代码块并确定其能够正确运行后，就可不必在上面花更多精力。确定函数能够正确地完成工作后，你就可以接着投身于下一个编程任务，因为你知道它们以后也不会出问题。

函数让你在编写一次代码后，可以复用它们任意多次。当需要运行函数中的代码时，只需编写一行函数调用代码，就能让函数完成其工作。当需要修改函数的行为时，只需修改一个代码块，你所做的修改就将影响调用这个函数的每个地方。

使用函数让程序更容易阅读，而良好的函数名概述了程序各个部分的作用。相比于阅读一系列代码块，阅读一系列函数调用让你能够更快地明白程序的作用。

函数还让代码更容易测试和调试。如果程序使用一系列函数来完成任务，其中的每个函数都完成一项具体工作，那么程序测试和维护起来将容易得多：可编写分别调用每个函数的程序，并测试每个函数是否在可能的各种情形下都能正确地运行。经过这样的测试，你就能深信每次调用这些函数时，它们都将正确地运行。

在第 9 章中，你将学习编写类。类将函数和数据整洁地封装起来，让你能够灵活而高效地使用它们。
