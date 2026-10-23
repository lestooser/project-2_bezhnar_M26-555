import prompt


def welcome() -> None:
    print("Первая попытка запустить проект!\n\n")
    print("***")
    print("<command> exit - выйти из программы")
    print("<command> help - справочная информация")
    command = prompt.string("Введите команду ")

    print(f"\nВы ввели команду {command}")
