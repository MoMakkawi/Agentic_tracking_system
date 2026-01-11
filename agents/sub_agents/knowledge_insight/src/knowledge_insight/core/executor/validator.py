import ast
from typing import List, Optional, Set
from utils import get_config
from .exceptions import ValidationError
from .defaults import DEFAULT_MODULES, DEFAULT_BUILTINS

class CodeValidator:
    """
    Validates Python code using AST analysis to ensure safe execution.
    Checks for forbidden imports, function calls, and attribute access.
    """

    def __init__(self, allowed_modules:Optional[List[str]] = None, forbidden_names: Optional[List[str]] = None):
        config = get_config().LLM_MODULES.KNOWLEDGE_INSIGHT.EXECUTOR_VALIDATORS.COMMON
        
        self.allowed_modules = allowed_modules or list(DEFAULT_MODULES.keys())
        self.forbidden_names = set(
            list(config.FORBIDDEN_NAMES) + (forbidden_names or [])
        )

    @staticmethod
    def _strip_preloaded_imports(code: str, allowed_modules: List[str]) -> str:
        """
        Remove import statements for pre-loaded modules.
        Since these modules are already available in the execution environment,
        imports are redundant and should be stripped.
        """
        lines = []
        for line in code.split('\n'):
            stripped = line.strip()
            
            # Check if line is an import statement for allowed modules
            if stripped.startswith(('import ', 'from ')):
                # Check if any allowed module is being imported
                is_allowed_import = False
                for module in allowed_modules:
                    if (f'import {module}' in stripped or 
                        f'from {module}' in stripped or
                        stripped.startswith(f'from {module}.')):
                        is_allowed_import = True
                        break
                
                # Skip this line if it's importing a pre-loaded module
                if is_allowed_import:
                    continue
            
            lines.append(line)
        
        return '\n'.join(lines)

    def validate(self, code: str) -> None:
        """
        Validate code using AST analysis.
        
        Args:
            code: Python code string to validate
            
        Raises:
            ValidationError: If unsafe code patterns are detected
            SyntaxError: If code has syntax errors
        """
        # Strip redundant imports for pre-loaded modules
        code = self._strip_preloaded_imports(code, self.allowed_modules)
        
        try:
            tree = ast.parse(code, mode='exec')
        except SyntaxError as e:
            raise ValidationError(f"Syntax error in code: {e}")

        for node in ast.walk(tree):
            self._check_imports(node)
            self._check_function_calls(node)
            self._check_attributes(node)

    def _check_imports(self, node: ast.AST) -> None:
        """
        Validate import statements.
        Only forbidden imports should reach here since allowed imports are stripped.
        """
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name not in self.allowed_modules:
                    raise ValidationError(
                        f"Import of module '{alias.name}' is forbidden. "
                        f"Available pre-loaded modules: {', '.join(self.allowed_modules)}"
                    )

        elif isinstance(node, ast.ImportFrom):
            if node.module and node.module not in self.allowed_modules:
                # Check base module for nested imports (e.g., 'collections.abc')
                base_module = node.module.split('.')[0]
                if base_module not in self.allowed_modules:
                    raise ValidationError(
                        f"Import from module '{node.module}' is forbidden. "
                        f"Available pre-loaded modules: {', '.join(self.allowed_modules)}"
                    )

    def _check_function_calls(self, node: ast.AST) -> None:
        """Validate function calls against forbidden list."""
        if not isinstance(node, ast.Call):
            return

        func_name = self._extract_function_name(node.func)
        if func_name and func_name in self.forbidden_names:
            raise ValidationError(
                f"Use of forbidden function '{func_name}' detected"
            )

    @staticmethod
    def _extract_function_name(func: ast.AST) -> Optional[str]:
        """Extract function name from AST node."""
        if isinstance(func, ast.Name):
            return func.id
        elif isinstance(func, ast.Attribute):
            return func.attr
        return None

    def _check_attributes(self, node: ast.AST) -> None:
        """Block access to dunder attributes."""
        if isinstance(node, ast.Attribute) and node.attr.startswith("__"):
            raise ValidationError(
                f"Access to dunder attribute '{node.attr}' is forbidden"
            )