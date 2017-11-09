import json

class DataParser:

    def __init__(self):
        # map paths to their respective data contents
        self.data = {}


    # parses a JSON file
    # returns the JSON object
    # stores it if store_data == True
    def parse(self, path, store_data = True):
        if path in self.data:
            return self.data[path]

        data = None

        try:
            with open(path) as data_file:
                data = json.load(data_file)
        except Exception:
            print 'error opening %s' % path
            return None

        if store_data:
            self.data[path] = data
        return data
