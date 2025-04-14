from abc import ABC, abstractmethod
from functools import wraps
from typing import Callable, Any
import random

class BinaryFieldNode(ABC):
    """
    The basic type of binary field.
    Use "BFN" as a shorter representation. 
    """
    @abstractmethod
    def __init__(self):
        """
        Initialize the function.
        """

        ###### For tree stucture ######

        # We use dict to store the BFNs
        # because we want to process the related BFNs according to their names。

        # the `children` dictionary must be ordered, 
        # because we may need to concatenate the binary expression of the chidren 
        # to get the binary expression of current BFN.
        self.children : dict[str,BinaryFieldNode] = {}
        self.parent : BinaryFieldNode = None

        ###### For the dependency relations ######

        # Dependency relationships only happen between siblings, 
        # and set by the parent via `add_dependency`.
        
        # the BFNs whose values decides the value of current BFN.
        self.dependencies = dict[str,BinaryFieldNode] = {}
        # the BFNs whose values depend on the value of current BFN.
        self.depend_on_me = dict[str,BinaryFieldNode] = {}

        ###### For modification ######

        # If the value of this BFN is detached from its dependencies
        # If `detached=True`, the current will not be updated 
        # when the `dependencies` are updated
        # Important:
        # When `detached=True`, the `binary_content` must be the value of 
        self.detached = False

        # This should be `None` unless you decided to modify the binary value of 
        # this BFN directly, which may break the semantic of the field.
        # After the binary value of the BFN is modified, `detached` must be set `True`
        self.binary_content : bytes = None

        # The prefix and suffix attached to the end of the field.
        self.prefix : bytes = b''
        self.suffix : bytes = b''

        ###### This function must be re-implemented ######

        raise NotImplementedError()

    ########## Get binary info ##########

    @abstractmethod
    def get_binary_expression_inner(self) -> bytes:
        """
        Get the binary expression of the BFN.
        If `self.binary_content` is not None, you sould return `self.binary_content`,
        otherwise you should return in your way. 
        For the reason of such design, you should refer to the 
        annotation of the set-function section. 
        """
        raise NotImplementedError()

    def get_binary_expression(self) -> bytes:
        """
        Get the final binary expression of the BFN.
        Attach the prefix and suffix on them. 
        If `self.binary_content` is not None, you sould return `self.binary_content` 
        (along with the prefix and suffix), otherwise you should return in your way.
        """
        if self.binary_content is not None:
            return self.prefix + self.binary_content + self.suffix
        return self.prefix + self.get_binary_expression_inner() + self.suffix

    def get_binary_length(self) -> int:
        """Get the length of the binary expression of this BFN."""
        return len(self.get_binary_expression())
    
    ########## Update according to dependencies ##########

    # TODO: Is this class useful?
    class BFNUpdateRule:
        """
        The update rule of class `BinaryFieldNode`
        Current the class is NOT used!
        """
        def __init__(self,
                     match_rule: Callable[[str], bool],
                     process_func: Callable[["BinaryFieldNode", "BinaryFieldNode"], None]):
            """
            Initialize the update rule.
            1. `match_rule` takes the key of the dependency key and check if 
               such dependency can match the corresponding processing function.
            2. `process_func` updates the BFN. 
            """
            self.match_rule = match_rule
            self.process_func = process_func
        
        def if_match(self, dependency_key: str):
            """
            Take the dependency key as input and check if that dependency match the process rule.
            """
            return self.match_rule(dependency_key)

        def process(self,
                    others_self : "BinaryFieldNode",
                    dependency : "BinaryFieldNode"):
            """
            Process the BFN according to the dependency. 
            """
            self.process_func(others_self,dependency)
    
    @abstractmethod
    def update_on_dependencies_inner(self):
        """
        The inner function called by `update_on_dependencies`.
        """
        raise NotImplementedError()
    
    def update_on_dependencies(self):
        """
        Update the current BFN according to its dependencies.
        Return `Ture` if there is some modification made to the binary expression of current BFN
        You should skip this function and return `False` if the current BFN is detached.
        """
        if self.detached:
            # detached, you should skip this time.
            return False
        # Clear the prefix and suffix.
        self.prefix = b''
        self.suffix = b''
        # Update inner
        previous_binary_val = self.get_binary_expression()
        self.update_on_dependencies_inner()
        now_binary_val = self.get_binary_expression()

        # return if you should recursively call the `update` function of other BFNs
        return now_binary_val==previous_binary_val

    def update_depend_on_me(self):
        """
        Update the BFNs depend on current BFN.
        parent node is not included in `depend_on_me`, 
        but is processed in `update_depend_on_me` function. 
        """
        for bfn in self.depend_on_me:
            bfn.update()
        self.parent.update()
    
    def update(self):
        """
        Update the current status of the BFN.
        First update yourself on the dependencies, 
        then recursively call the 
        """
        updated = self.update_on_dependencies()
        if updated:
            # You should recursively call the `update` functions 
            self.update_depend_on_me()
    
    def detach(self):
        """Let the BFN detached from its dependencies."""
        self.detached = True

    def attach(self):
        """
        Let the BFN attach again to its dependencies.
        Notice: Once you attach again, the modifications you made will disappear.
        """
        self.detached = False
        # Call update function.
        # The clearance of prefix and suffix will happen inside the `update` function
        self.update()
    
    def if_detached(self):
        """Return if the current BFN is detached."""
        return self.detached
    
    ########## Manage relationships ##########

    def append_child(self, 
                     child: "BinaryFieldNode",
                     child_key: str):
        """
        Append a child to `self.children`.
        Recall that the children must be ordered.
        """
        if child_key in self.children:
            print(f"Child key {child_key} has been used, please change one.")
        self.children[child_key] = child

    def remove_child(self, child_key: str):
        """Remove a child with given key."""
        if child_key in self.children:
            self.children.pop(child_key)
    
    def set_parent(self, parent: "BinaryFieldNode"):
        """
        Set the parent node of current node.
        This is NOT a set-function (which will be mentioned later)
        """
        self.parent = parent

    ########## Manage dependencies ##########

    def append_dependency(self, 
                          dependency: "BinaryFieldNode",
                          dependency_key: str):
        """Append a dependency to `self.dependencies`."""
        if dependency_key in self.dependencies:
            print(f"Dependency key {dependency_key} has been used, please change one.")
        self.dependencies[dependency_key] = dependency
    
    def remove_dependency(self, dependency_key: str):
        """Remove a dependency with given key."""
        if dependency_key in self.dependencies:
            self.dependencies.pop(dependency_key)
        
    def append_depend_on_me(self,
                            depend_on_me: "BinaryFieldNode",
                            depend_on_me_key: str):
        """Append a depend-on-me to `self.depend_on_me`."""
        if depend_on_me_key in self.dependencies:
            print(f"Dependent-on-me key {depend_on_me_key} has been used, please change one.")
        self.depend_on_me[depend_on_me_key] = depend_on_me

    def remove_depend_on_me(self, depend_on_me_key: str):
        """Remove a depend-on-me with given key."""
        if depend_on_me_key in self.depend_on_me:
            self.depend_on_me.pop(depend_on_me_key)
    
    def add_dependency(self,
                       dependent_key: str,
                       dependency_key: str):
        """
        Add dependency between two CHILDREN.
        `dependent_key` depends on `dependency_key`.
        """
        if dependent_key not in self.children:
            print(f"Child {dependent_key} is not in the children of the BFN.") 
            return
        if dependency_key not in self.children:
            print(f"Child {dependency_key} is not in the children of the BFN.") 
            return
        self.children[dependent_key].append_dependency(self.children[dependency_key],
                                                       dependency_key)
        self.children[dependency_key].append_depend_on_me(self.children[dependent_key],
                                                          dependent_key)
    
    def remove_depencency(self,
                          dependent_key: str,
                          dependency_key: str):
        """
        Remove dependency between two CHILDREN.
        `dependent_key` depends on `dependency_key`.
        """
        if dependent_key not in self.children:
            print(f"Child {dependent_key} is not in the children of the BFN.") 
            return
        if dependency_key not in self.children:
            print(f"Child {dependency_key} is not in the children of the BFN.") 
            return
        self.children[dependent_key].remove_depencency(self.children[dependency_key],
                                                       dependency_key)
        self.children[dependency_key].remove_depend_on_me(self.children[dependent_key],
                                                          dependent_key)

    ############################################################
    #    The following section is about the mutation of BFN    #
    ############################################################

    ########## Methods for generating random mutation ##########
    
    # These functions should be class methods 

    @classmethod
    def random_bval_fixed_len(cls,
                              length: int):
        """Generate a random binary value with fixed length."""
        return random.randbytes(length)

    @classmethod
    def random_bval(cls,
                    max_length: int = 15):
        """
        Generate a random binary value. 
        The length is uniformly sampled from [0, max_length]
        """
        length = random.randint(0,max_length)
        return cls.random_bval_fixed_len(length)

    ########## Methods for applying mutation ##########

    # These functions are used to set the value of the BFN. 
    # You should only call these functions to modify BFN, 
    # but you should not use these methods to build other functionalities, 
    # because all setting methods involve decorated operations like 
    # detach, update, etc.

    ###### Overwriting rules of set-functions ###### 
    #
    # There are three categories of set-functions:
    # 1. `set_bval`: set the binary value of the BFN directly
    # 2. `set_prefix` and `set_suffix`: set the prefix and suffix of the 
    #    BFN's binary expression.
    # 3. Other set-functions modifying other properties of the BFN.
    # 
    # When you call them in different order, 
    # their effects will be overwritten in different ways,
    # which is shown in the following table:
    # 
    # ______________| set_bv | set_pref/suff | set_others |
    # set_bv        |    O   |       O       |     O      |
    # set_pref/suff |    X   |       O       |     X      |
    # set_others    |    O   |       X       |     O      |
    #
    # Such rules are embeded in the decorator `set_function_decorator`

    @staticmethod
    def set_function_decorator(func):
        """
        Represent the standard process of all set-function of BFN. 
        You should decorate all set-function with this decorator. 
        Following are the things should be done
        1. Detach from `self.dependencies`
        2. Update `self.depend_on_me` and `self.parent`
        3. Embed the overwriting rules of set-functions
           (So you do not need to worry about that in the set-function's).
        """
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            # First detach.
            self.detach()
            # Then embed the set-function overwriting rules
            if func.__name__ != "set_prefix" and func.__name__ != "set_suffix":
                self.binary_content = None
            if func.__name__ == "set_bval":
                self.prefix = b''
                self.suffix = b''
            # Then execute the set-functions
            result = func(self, *args, **kwargs)
            # Then update the BFNs depend on myself.
            self.update_depend_on_me()
            return result
        return wrapper

    def set_bval(self, binary_value: bytes):
        """
        Set the binary value of the BFN.
        """
        # Modify the binary content
        self.binary_content = binary_value

    def set_prefix(self, prefix:bytes):
        """
        Set the prefix of the binary expression. 
        """
        self.prefix = prefix

    def set_suffix(self, suffix:bytes):
        """
        Set the suffix of the binary expression. 
        """
        self.suffix = suffix
    
    ########## Method for generating mutation ##########

    # TODO: Finish this. 

    class MutationItem:
        """
        The class used for mutations.
        """
        def __init__(self,
                     random_generator: Callable[[Type[BFN]], Any],
                     setter: Callable[[Any], None]):
            """
            Initialize the `MutationItem`.
            `random_generator` takes the class and return the generated value.
            `setter` takes the class instance and values generated by `random_generator`
            """
            self.random_generator = random_generator
            self.setter = setter
        
        def set(self, others_self, )
