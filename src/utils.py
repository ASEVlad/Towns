import platform
import os


def get_geckodriver_path():
    system = platform.system()
    architecture = platform.machine()
    driver_path = select_driver_executable(system, architecture)

    return driver_path


def select_driver_executable(system, architecture):
    if system == 'Windows':
        executable_name = 'chromedriver.exe' if '64' in architecture else 'chromedriver_x86.exe'
    elif system == 'Darwin' or (system == 'Linux' and '64' in architecture):
        executable_name = 'chromedriver'
    else:
        raise ValueError("Unsupported operating system or architecture")

    executable_path = os.path.join("data", executable_name)

    if system != 'Windows':
        os.chmod(executable_path, 0o755)

    return executable_path


def get_full_xpath_element(driver, element):
    full_xpath_element= driver.execute_script(
        """function absoluteXPath(element) {
            var comp, comps = [];
            var parent = null;
            var xpath = '';
            var getPos = function(element) {
                var position = 1, curNode;
                if (element.nodeType == Node.ATTRIBUTE_NODE) {
                    return null;
                }
                for (curNode = element.previousSibling; curNode; curNode = curNode.previousSibling) {
                    if (curNode.nodeName == element.nodeName) {
                        ++position;
                    }
                }
                return position;
            };
            if (element instanceof Document) {
                return '/';
            }
            for (; element && !(element instanceof Document); element = element.nodeType == Node.ATTRIBUTE_NODE ? element.ownerElement : element.parentNode) {
                comp = comps[comps.length] = {};
                comp.name = element.nodeName;
                comp.position = getPos(element);
            }
            for (var i = comps.length - 1; i >= 0; i--) {
                comp = comps[i];
                xpath += '/' + comp.name.toLowerCase() + (comp.position > 1 ? '[' + comp.position + ']' : '');
            }
            return xpath;
        }
        return absoluteXPath(arguments[0]);""",
        element
    )
    return full_xpath_element
