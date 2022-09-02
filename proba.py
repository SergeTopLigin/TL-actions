import os
print(os.path.abspath(__file__))

# Чтобы поиск файла всегда производился в каталоге с исполняемым файлом, необходимо этот каталог сделать текущим с помощью
#os.chdir(os.path.dirname(os.path.abspath(__file__)))

f = open("file.txt", "w")
f.write("Строка") # Записываем строку в файл
f. close ()
