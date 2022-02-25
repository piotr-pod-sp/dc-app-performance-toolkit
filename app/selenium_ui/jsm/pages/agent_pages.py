import random

from selenium_ui.base_page import BasePage
from selenium.webdriver.common.keys import Keys
from selenium_ui.jsm.pages.agent_selectors import LoginPageLocators, PopupLocators, DashboardLocators, LogoutLocators, \
    BrowseProjectsLocators, BrowseCustomersLocators, ViewCustomerRequestLocators, UrlManager, ViewReportsLocators, \
    ViewQueueLocators, InsightLocators


class PopupManager(BasePage):

    def dismiss_default_popup(self):
        return self.dismiss_popup(PopupLocators.default_popup, PopupLocators.popup_1, PopupLocators.popup_2,
                                  PopupLocators.popup_3, PopupLocators.popup_4,
                                  PopupLocators.popup_5)


class Login(BasePage):
    page_url = LoginPageLocators.login_url
    page_loaded_selector = LoginPageLocators.system_dashboard

    def is_first_login(self):
        return True if self.get_elements(LoginPageLocators.continue_button) else False

    def is_first_login_second_page(self):
        return True if self.get_elements(LoginPageLocators.avatar_page_next_button) else False

    def first_login_setup(self):
        self.wait_until_visible(LoginPageLocators.continue_button).send_keys(Keys.ESCAPE)
        self.get_element(LoginPageLocators.continue_button).click()
        self.first_login_second_page_setup()

    def first_login_second_page_setup(self):
        self.wait_until_visible(LoginPageLocators.avatar_page_next_button).click()
        self.wait_until_visible(LoginPageLocators.explore_current_projects).click()
        self.go_to_url(DashboardLocators.dashboard_url)
        self.wait_until_visible(DashboardLocators.dashboard_window)

    def set_credentials(self, username, password):
        self.get_element(LoginPageLocators.login_field).send_keys(username)
        self.get_element(LoginPageLocators.password_field).send_keys(password)
        self.get_element(LoginPageLocators.login_submit_button).click()

    def __get_footer_text(self):
        return self.get_element(LoginPageLocators.footer).text

    def get_app_version(self):
        text = self.__get_footer_text()
        return text.split('#')[0].replace('(v', '')

    def get_node_id(self):
        text = self.get_element(LoginPageLocators.footer).text
        text_split = text.split(':')
        if len(text_split) == 2:
            return "SERVER"
        elif len(text_split) == 3:
            return text_split[2].replace(')', '')
        else:
            return f"Warning: failed to get the node information from '{text}'."


class Logout(BasePage):
    page_url = LogoutLocators.logout_url

    def click_logout(self):
        self.get_element(LogoutLocators.logout_submit_button).click()

    def wait_for_page_loaded(self):
        self.wait_until_present(LogoutLocators.login_button_link)


class BrowseProjects(BasePage):
    page_url = BrowseProjectsLocators.brows_projects_url

    def wait_for_page_loaded(self):
        self.wait_until_visible(BrowseProjectsLocators.page_title)


class BrowseCustomers(BasePage):

    def __init__(self, driver, project_key=None):
        BasePage.__init__(self, driver)
        url_manager = UrlManager(project_key=project_key)
        self.page_url = url_manager.browse_project_customers_page_url()

    def wait_for_page_loaded(self):
        self.wait_until_visible(BrowseCustomersLocators.page_title)


class ViewCustomerRequest(BasePage):
    timeout = 30

    def __init__(self, driver, request_key=None):
        BasePage.__init__(self, driver)
        url_manager = UrlManager(request_key=request_key)
        self.page_url = url_manager.view_customer_request_url()

    def wait_for_page_loaded(self):
        self.wait_until_visible(ViewCustomerRequestLocators.bread_crumbs)

    def check_comment_text_is_displayed(self, text, rte_status=None):
        if self.get_elements(ViewCustomerRequestLocators.comment_text_field_RTE) or \
                self.get_elements(ViewCustomerRequestLocators.comment_text_field):
            if rte_status:
                self.wait_until_available_to_switch(ViewCustomerRequestLocators.comment_text_field_RTE)
                if self.wait_until_present(ViewCustomerRequestLocators.comment_tinymce_field).text != text:
                    self.wait_until_present(ViewCustomerRequestLocators.comment_tinymce_field).send_keys(text)
                    self.return_to_parent_frame()
                    self.wait_until_present(ViewCustomerRequestLocators.comment_internally_btn).click()
            elif self.wait_until_present(ViewCustomerRequestLocators.comment_text_field).text != text:
                self.wait_until_present(ViewCustomerRequestLocators.comment_text_field).send_keys(text)
                self.wait_until_present(ViewCustomerRequestLocators.comment_internally_btn).click()

    def add_request_comment(self, rte_status):
        comment_text = f"Add comment from selenium - {self.generate_random_string(30)}"
        textarea = self.get_element(ViewCustomerRequestLocators.comment_collapsed_textarea)
        self.driver.execute_script("arguments[0].scrollIntoView(true);", textarea)
        textarea.click()
        comment_button = self.get_element(ViewCustomerRequestLocators.comment_internally_btn)
        self.driver.execute_script("arguments[0].scrollIntoView(true);", comment_button)

        if rte_status:
            self.wait_until_available_to_switch(ViewCustomerRequestLocators.comment_text_field_RTE)
            self.wait_until_present(ViewCustomerRequestLocators.comment_tinymce_field).send_keys(comment_text)
            self.return_to_parent_frame()
            comment_button.click()
            self.check_comment_text_is_displayed(comment_text, True)
        else:
            self.wait_until_present(ViewCustomerRequestLocators.comment_text_field).send_keys(comment_text)
            comment_button.click()
            self.check_comment_text_is_displayed(comment_text)


class Report:

    @staticmethod
    def view_workload_report(driver, project_key):
        return WorkloadReport(driver, project_key)

    @staticmethod
    def view_time_to_resolution_report(driver, project_key, time_to_resolution_report_id):
        return TimeToResolutionReport(driver, project_key, time_to_resolution_report_id)

    @staticmethod
    def view_created_vs_resolved_report(driver, project_key, created_vs_resolved_report_id):
        return CreatedResolvedReport(driver, project_key, created_vs_resolved_report_id)


class WorkloadReport(BasePage):
    page_loaded_selector = ViewReportsLocators.team_workload_agents_table
    timeout = 60

    def __init__(self, driver, project_key=None):
        BasePage.__init__(self, driver)
        url_manager = UrlManager(project_key=project_key)
        self.page_url = url_manager.workload_report_url()


class TimeToResolutionReport(BasePage):
    page_loaded_selector = ViewReportsLocators.custom_report_content
    timeout = 60

    def __init__(self, driver, project_key, time_to_resolution_report_id):
        BasePage.__init__(self, driver)
        url_manager = UrlManager(project_key=project_key, custom_report_id=time_to_resolution_report_id)
        self.page_url = url_manager.custom_report_url()


class CreatedResolvedReport(BasePage):
    page_loaded_selector = ViewReportsLocators.custom_report_content
    timeout = 60

    def __init__(self, driver, project_key, time_to_resolution_report_id):
        BasePage.__init__(self, driver)
        url_manager = UrlManager(project_key=project_key, custom_report_id=time_to_resolution_report_id)
        self.page_url = url_manager.custom_report_url()


class ViewQueue(BasePage):
    timeout = 60

    def __init__(self, driver, project_key=None, queue_id=None):
        BasePage.__init__(self, driver)
        url_manager = UrlManager(project_key=project_key, queue_id=queue_id)
        self.page_url = url_manager.view_queue_all_open()

    def wait_for_page_loaded(self):
        self.wait_until_any_ec_presented(
            selectors=[ViewQueueLocators.queues_status, ViewQueueLocators.queue_is_empty], timeout=self.timeout)

    def get_random_queue(self):
        if not self.get_elements(ViewQueueLocators.queue_is_empty):
            queues = self.get_elements(ViewQueueLocators.queues)
            random_queue = random.choice([queue for queue in queues
                                          if queue.text.partition('\n')[0] not in
                                          ['All open', 'Recently resolved', 'Resolved past 7 days']
                                          and queue.text.partition('\n')[2] != '0'])
            random_queue.click()
            self.wait_until_present(ViewQueueLocators.queues_status, timeout=self.timeout)


class InsightLogin(BasePage):
    dashboard_url = UrlManager().dashboard_url()

    def insight_schema(self):
        self.wait_until_clickable(InsightLocators.insight_dropdown).click()
        self.wait_until_visible(InsightLocators.insight_object_schemas_button).click()

    # #sumbit login required to start working with insight
    def submit_login(self, username, password):
        self.get_element(LoginPageLocators.login_field).send_keys(username)
        self.get_element(LoginPageLocators.password_field).send_keys(password)
        self.get_element(LoginPageLocators.login_submit_button).click()


class InsightNewSchema(BasePage):

    def create_new_schema(self):
        new_schema_name = self.generate_random_string(10)
        if not self.get_elements(InsightLocators.insight_dialog_news):
            self.wait_until_visible(InsightLocators.create_object_schemas)
            if self.get_elements(InsightLocators.insight_dialog_news):
                self.wait_until_clickable(InsightLocators.insight_dialog_news).click()
        self.wait_until_visible(InsightLocators.create_object_schemas).click()
        self.wait_until_visible(InsightLocators.new_object_schema)
        self.wait_until_visible(InsightLocators.new_object_schema).click()
        self.wait_until_clickable(InsightLocators.object_schemas_next_button).click()
        self.get_element(InsightLocators.object_schemas_name_field).send_keys(new_schema_name)
        self.wait_until_clickable(InsightLocators.object_schemas_create_button).click()
        self.wait_until_invisible(InsightLocators.object_schemas_name_field)
        self.wait_until_visible(InsightLocators.create_object_schemas)

        return new_schema_name

    # вот здесь добавить создание обьекта, чтоб это была одна функция за другой и мы чистили дату

    def delete_new_schema(self, schema_name):  # перейти на страницу /каждая страничка должна быть отдельно
        delete_schema_locator = InsightLocators.delete_schema[1] + schema_name
        self.wait_until_clickable(InsightLocators.insight_dropdown).click()
        self.wait_until_visible(InsightLocators.insight_object_schemas_button).click()
        self.wait_until_visible(InsightLocators.create_object_schemas)
        # self.action_chains().move_to_element(self.get_element(InsightLocators.object_count_selector)).perform()
        self.get_element(InsightLocators.object_schemas_created)
        self.execute_js(f"document.getElementById('{delete_schema_locator}').click()")
        self.wait_until_visible(InsightLocators.delete_window_selector)
        self.wait_until_clickable(InsightLocators.submit_delete_button).click()
        self.wait_until_clickable(InsightLocators.submit_delete_button).click()
        self.wait_until_invisible(InsightLocators.submit_delete_button)


class InsightNewObject(BasePage):

    def __init__(self, driver, schema_id=None):
        BasePage.__init__(self, driver)
        url_manager = UrlManager(schema_id=schema_id)
        self.page_url = url_manager.view_insight_schema()

    def insight_create_new_objects(self):
        if not self.get_elements(InsightLocators.insight_dialog_news):
            self.wait_until_visible(InsightLocators.create_object_button)
            if self.get_elements(InsightLocators.insight_dialog_news):
                self.wait_until_clickable(InsightLocators.insight_dialog_news).click()
        self.wait_until_visible(InsightLocators.create_object_button).click()
        self.wait_until_visible(InsightLocators.object_name_field)
        self.get_element(InsightLocators.object_name_field).send_keys(self.generate_random_string(10))
        self.wait_until_visible(InsightLocators.create_button)
        self.wait_until_visible(InsightLocators.create_button).click()
        self.wait_until_invisible(InsightLocators.pop_up_after_create_object)


class InsightViewQueue(BasePage):

    def __init__(self, driver, project_key=None):
        BasePage.__init__(self, driver)
        url_manager = UrlManager(project_key=project_key)
        self.page_url = url_manager.view_insight_queue()

    def wait_for_page_loaded(self):
        self.wait_until_visible(InsightLocators.view_queue_page)

    def view_random_queue_with_insight(self):
        self.wait_until_visible(InsightLocators.view_queue_insight_column)


class InsightSearchObjectIql(BasePage):

    def search_object_by_iql(self):
        iql_attribute_search = f'Name >= {self.generate_random_string(2)}'
        self.wait_until_clickable(InsightLocators.insight_dropdown).click()
        self.wait_until_visible(InsightLocators.search_object_by_iql).click()
        self.wait_until_visible(InsightLocators.search_object_text_field)
        self.get_element(InsightLocators.search_object_text_field).send_keys(iql_attribute_search)
        self.wait_until_visible(InsightLocators.search_iql_button).click()
        self.wait_until_visible(InsightLocators.search_iql_success)


class ViewIssueWithObject(BasePage):

    def __init__(self, driver, insight_issues=None):
        BasePage.__init__(self, driver)
        url_manager = UrlManager(insight_issues=insight_issues)
        self.page_url = url_manager.view_issue_with_object()

    def wait_for_page_loaded(self):
        self.wait_until_visible(InsightLocators.issue_title)

    def view_issue_with_insight_custom_field(self):
        self.wait_until_visible(InsightLocators.custom_field_insight)
