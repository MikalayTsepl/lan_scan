class TabelWriter:
    file_name = ''
    input = []

    def __init__(self, file_name, input):
        self.file_name = file_name
        self.input.extend(input)
        with open(f'Outputs/{self.file_name}.txt',
                  "w+") as file:
            for row in self.input:
                for element in row:
                    file.write(f'{element} ')
                file.write('\n')
