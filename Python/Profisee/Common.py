import uuid, logging
from functools import wraps

from pyparsing import Any

null_guid = uuid.UUID('{00000000-0000-0000-0000-000000000000}')

class Common() :
    """Holds common static functions to be used by other modules.
    """
    @staticmethod
    def LogFunction(func) :
        """Decorator that will collect the calling information and send to logging as a debug statement.

        Args:
            func (definition): Original function call.

        Returns:
            any: Return from original function being called.
        """
        @wraps(func)
        def out(*args, **kwargs) :
            parameterList = []        
            if args != None : 
                args1 = args[1:] # To strip off self, need a better way to do this to make it generic...
                parameterList.append(str(args1).strip('(),'))
            if kwargs != None and len(kwargs) > 0 : parameterList.append(str(kwargs).strip('{}'))
            parameters = ', '.join(parameterList)

            logging.getLogger().info(f"{func.__name__}({parameters})")
            return func(*args, **kwargs)
        return out

    @staticmethod
    def __first(iterable, condition = lambda default : True) :
        """Returns first element from iterable.

        Args:
            iterable (_type_): Iterable that will searched for condition.
            condition (lambda): lambda function for element to pass. Defaults to lambda default:True.

        Returns:
            element: Element if condition found or None.
        """
        for item in iterable :
            if condition(item) : return item
        return None
        
    @staticmethod
    def Set(node, name, value) :
        """_summary_

        Args:
            node (_type_): _description_
            name (_type_): _description_
            value (_type_): _description_
        """
        if node != None :
            key = Common.__first(node.keys(), lambda k : k.lower() == name.lower())
            if key != None : node[key] = value
            else           : node[name] = value
        
    @staticmethod
    def Get(node, name: str, default: Any = None) -> Any :
        """_summary_

        Args:
            node (_type_): _description_
            name (_type_): _description_

        Returns:
            _type_: _description_
        """
        # if node != None :
        #     key = Common.__first(node.keys(), lambda k : k.lower() == name.lower())
        #     if key != None : return node[key]
        # return default 
    
        if node == None: return default

        if "/" in name: # Handle Paths
            for name in name.split("/"):
                node = Common.Get(node, name)
            return node if node != None else default         
        else:    
            key = Common.__first(node.keys(), lambda k: k.lower() == name.lower())
            return node[key] if key!= None else default