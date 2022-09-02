import os
print(os.path.abspath(__file__))

#os.chdir(os.path.dirname(os.path.abspath(__file__)))

f = open("file.txt", "w")
f.write("Строка") # Записываем строку в файл
f. close ()
