import abc

class tag_strategy_manager():
    @staticmethod
    def get_tag_strategy(tag):
        f =  {"title":title_tag_strategy()}
        return f[tag]

class tag_strategy(abc.ABC):
    @abc.abstractmethod
    @staticmethod
    def execute(self):
        pass

class title_tag_strategy(tag_strategy):
    @staticmethod
    def execute(self):
        print("are you kidding me? You didn't put real code here?")
        return {"title_sect":'content'}


# title_tag_strategy.execute()