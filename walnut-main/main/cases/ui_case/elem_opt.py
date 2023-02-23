from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement


def is_exist(d: WebDriver, loc: str) -> bool:
    '''元素是否存在'''
    try:
        elem = d.find_element(loc)
        return True
    except Exception as e:
        return False


def is_in_elem(el: WebElement, xpath):
    try:
        el.find_element(By.XPATH, xpath)
        return True
    except Exception as e:
        return False


def get_text(e: WebElement):
    try:
        t = e.get_attribute('textContent')
        return t
    except Exception as e:
        return ''


class OnesRedio:
    """单选按钮"""

    _radio = None

    def __init__(self, driver: WebDriver, name):
        self.name = name
        self.driver = driver
        self.locator = f'//span[text()="{name}"]/../following-sibling::div[1]'
        try:
            self._radio = self.driver.find_element(self.locator)
        except Exception as e:
            raise ValueError('单选按钮不存在')

    def get_options(self):
        """
        获取选项值
        :return:
        """
        try:
            oes = self._radio.find_elements(By.XPATH,
                                            './/label/span[contains(@class, "ones-radio")]/following-sibling::span[1]')
            ops = [o.get_attribute('textContent') for o in oes]
            return ops
        except Exception as e:
            return []

    def option_checked(self):
        """
        选中的选项
        :return: 选项名
        """
        try:
            op = self._radio.find_element(By.XPATH, './/label/span[contains(@class, "ones-radio-checked")]'
                                                    '/following-sibling::span[1]')
            tx = op.get_attribute('textContent')
            return tx
        except Exception as e:
            return ''
            # raise ValueError(e)


class OnesSelect:
    """单选框"""
    _select = None

    def __init__(self, driver: WebDriver, name):
        self.name = name
        self.driver = driver
        self.locator = '//span[text()="%s"]/following-sibling::div[1]' % (name)
        try:
            self._select = self.driver.find_element(self.locator)
        except Exception as e:
            raise ValueError('单选框不存在')

    def get_value(self):
        try:
            tx = self._select.find_element(By.XPATH, 'div/div/div').get_attribute('textContent')
            return tx
        except Exception:
            return ''

    def get_options(self):
        try:
            self._select.click()
            # '//div[contains(@class, "ant-select-dropdown ant-select-dropdown--single ant-select-dropdown-placement-bottomLeft") and not(contains(@class, "ant-select-dropdown-hidden"))]/div/ul/li'
            ops = self.driver.find_elements(
                "//div[@class='ant-select-dropdown ant-select-dropdown--single ant-select-dropdown-placement-bottomLeft']/div/ul/li")
            op_tx = [p.get_attribute('textContent') for p in ops]
            self._select.click()
            return op_tx
        except Exception as e:
            return []
