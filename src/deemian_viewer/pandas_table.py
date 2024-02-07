class PandasReactTableModel():
    def __init__(self):
        self.data_all = []
        self.current_data = []
    
    def __len__(self):
        return len(self.current_data)
    
    def register_table(self, name, data, conf=1):
        current_data = [list(row) for row in data[data["conformation"] == conf].itertuples()]

        self.data_all.append({"name": name, "data": data})
        self.current_data.append({"name": name, "current_data": current_data})
    
    def set_frame(self, conf):
        for i, data in enumerate(self.data_all):
            data = data["data"]
            current_data = [list(row) for row in data[data["conformation"] == conf].itertuples()]
            self.current_data[i]["current_data"] = current_data
    
    def get_data(self, index):
        return self.current_data[index]
