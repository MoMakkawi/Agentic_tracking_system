import json
from typing import Any, Dict, Optional
from utils import logger
from .exceptions import ValidationError
from .namespace import NamespaceBuilder
from .validator import CodeValidator

class CodeExecutor:
    """
    Safely executes dynamically generated Python code in a controlled environment.
    Validates code before execution and manages namespace isolation.
    """

    def __init__(
        self,
        validator: Optional[CodeValidator] = None,
        modules: Optional[Dict[str, Any]] = None,
        builtins: Optional[Dict[str, Any]] = None,
        helpers: Optional[Dict[str, Any]] = None,
        datasets: Optional[Dict[str, Any]] = None
    ):
        # Initialize validator with module names
        module_names = list((modules or {}).keys())
        self.validator = validator or CodeValidator(allowed_modules=module_names)
        
        self.namespace_builder = NamespaceBuilder(
            modules=modules,
            helpers=helpers,
            datasets=datasets,
            builtins=builtins
        )

    def execute(self, code: str) -> str:
        """
        Validate and execute Python code safely.
        
        Args:
            code: Python code string that must assign result to 'result' variable
            
        Returns:
            String representation of the result (JSON for dicts/lists)
            
        Raises:
            ExecutionError: If code execution fails
        """
        try:
            self.validator.validate(code)
            namespace = self.namespace_builder.build()
            
            exec(code, namespace)
            
            return self._format_result(namespace.get("result"))
            
        except ValidationError as e:
            msg = f"CODE VALIDATION ERROR: {e}"
            raise Exception(msg)
            
        except NameError as e:
            msg = f"NAME ERROR: {e}"
            raise Exception(msg)
            
        except Exception as e:
            msg = f"EXECUTION ERROR: {type(e).__name__}: {e}"
            raise Exception(msg)

    @staticmethod
    def _format_result(result: Any) -> str:
        """
        Format execution result as string.
        
        Args:
            result: The value assigned to 'result' variable
            
        Returns:
            Formatted string representation
        """
        if result is None:
            return "ERROR: Code executed but 'result' variable was not assigned"
            
        if isinstance(result, (dict, list)):
            return json.dumps(result, indent=2, ensure_ascii=False)
            
        return str(result)