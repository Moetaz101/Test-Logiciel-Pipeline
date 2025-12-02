"""
Selenium Automation Tests for DemoQA Books Page
Tests automated: Search, Case Sensitivity, Navigation, SQL Injection, Sorting
"""

# ============================================================================
# IMPORTS
# ============================================================================
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import os
from datetime import datetime

# ============================================================================
# MAIN TEST CLASS
# ============================================================================
class DemoQABooksTests:
    # ========================================================================
    # INITIALIZATION
    # ========================================================================
    def __init__(self):
        # Configure Chrome options for headless mode
        chrome_options = Options()
        chrome_options.add_argument('--headless=new')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        
        # Initialize WebDriver with options
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.maximize_window()
        self.wait = WebDriverWait(self.driver, 10)
        self.url = "https://demoqa.com/books"
        self.results = []
        
        # Create screenshots folder
        self.screenshot_dir = os.path.join(os.getcwd(), "test_screenshots")
        os.makedirs(self.screenshot_dir, exist_ok=True)
        
    # ========================================================================
    # UTILITY METHODS
    # ========================================================================
    def take_screenshot(self, test_name):
        """Take screenshot on test failure"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{test_name}_{timestamp}.png"
        filepath = os.path.join(self.screenshot_dir, filename)
        self.driver.save_screenshot(filepath)
        print(f"   📸 Screenshot saved: {filename}")
        
    def log_result(self, test_id, test_name, passed, message=""):
        """Log test result"""
        status = "✅ PASS" if passed else "❌ FAIL"
        self.results.append({
            "id": test_id,
            "name": test_name,
            "status": status,
            "message": message
        })
        print(f"\n{status} - {test_id}: {test_name}")
        if message:
            print(f"   ℹ️  {message}")
        if not passed:
            self.take_screenshot(test_id)
            
    def get_search_input(self):
        """Get search input element"""
        try:
            return self.wait.until(EC.presence_of_element_located((By.ID, "searchBox")))
        except TimeoutException:
            return None
    
    def clear_search(self):
        """Clear search input safely"""
        try:
            search_input = self.get_search_input()
            if search_input:
                search_input.clear()
                time.sleep(0.5)
        except:
            self.driver.get(self.url)
            time.sleep(1)
    
    def get_book_elements(self):
        """Get all displayed book elements"""
        return self.driver.find_elements(By.CSS_SELECTOR, ".rt-tr-group")
    
    # ========================================================================
    # TEST CASE 01 - SEARCH BOOK COVER CONSISTENCY
    # ========================================================================
    def test_01_search_book_cover_consistency(self):
        """TC-001: Search book and verify cover consistency"""
        test_id = "TC-001"
        test_name = "Rechercher un livre et vérifier cohérence des couvertures"
        
        try:
            self.driver.get(self.url)
            time.sleep(2)
            
            initial_books = self.get_book_elements()
            initial_covers = {}
            
            for book in initial_books[:5]:
                try:
                    title_elem = book.find_element(By.CSS_SELECTOR, ".rt-td:nth-child(2) span")
                    img_elem = book.find_element(By.CSS_SELECTOR, "img")
                    title = title_elem.text.strip()
                    img_src = img_elem.get_attribute("src")
                    if title and img_src:
                        initial_covers[title] = img_src
                except:
                    continue
            
            if not initial_covers:
                self.log_result(test_id, test_name, False, "Aucun livre trouvé dans la liste initiale")
                return
                
            search_title = "Learning JavaScript Design Patterns"
            if search_title not in initial_covers:
                search_title = list(initial_covers.keys())[0]
            search_input = self.get_search_input()
            search_input.send_keys(search_title)
            time.sleep(1)
            
            filtered_books = self.get_book_elements()
            filtered_cover = None
            
            for book in filtered_books:
                try:
                    title_elem = book.find_element(By.CSS_SELECTOR, ".rt-td:nth-child(2) span")
                    if title_elem.text.strip() == search_title:
                        img_elem = book.find_element(By.CSS_SELECTOR, "img")
                        filtered_cover = img_elem.get_attribute("src")
                        break
                except:
                    continue
            
            if filtered_cover and filtered_cover == initial_covers[search_title]:
                self.log_result(test_id, test_name, True, f"Couverture cohérente pour '{search_title}'")
            else:
                self.log_result(test_id, test_name, False, f"Couverture différente ou non trouvée pour '{search_title}'")
                
        except Exception as e:
            self.log_result(test_id, test_name, False, f"Erreur: {str(e)}")
        finally:
            self.clear_search()
            
    # ========================================================================
    # TEST CASE 02 - CASE INSENSITIVE SEARCH
    # ========================================================================
    def test_02_case_insensitive_search(self):
        """TC-002: Verify case-insensitive search"""
        test_id = "TC-002"
        test_name = "Recherche insensible à la casse"
        
        try:
            self.driver.get(self.url)
            time.sleep(2)
            
            search_term = "Git"
            
            search_input = self.get_search_input()
            search_input.send_keys(search_term.upper())
            time.sleep(1)
            upper_results = len([b for b in self.get_book_elements() if b.text.strip()])
            self.clear_search()
            
            search_input = self.get_search_input()
            search_input.send_keys(search_term.lower())
            time.sleep(1)
            lower_results = len([b for b in self.get_book_elements() if b.text.strip()])
            self.clear_search()
            
            search_input = self.get_search_input()
            search_input.send_keys("gIt")
            time.sleep(1)
            mixed_results = len([b for b in self.get_book_elements() if b.text.strip()])
            
            if upper_results == lower_results == mixed_results and upper_results > 0:
                self.log_result(test_id, test_name, True, f"Tous retournent {upper_results} résultat(s)")
            else:
                self.log_result(test_id, test_name, False, f"Résultats différents: MAJ={upper_results}, min={lower_results}, mixte={mixed_results}")
                
        except Exception as e:
            self.log_result(test_id, test_name, False, f"Erreur: {str(e)}")
        finally:
            self.clear_search()
            
    # ========================================================================
    # TEST CASE 03 - CLICK BOOK NAVIGATION
    # ========================================================================
    def test_03_click_book_navigation(self):
        """TC-003: Click book title and verify navigation"""
        test_id = "TC-003"
        test_name = "Navigation vers page de détails du livre"
        
        try:
            self.driver.get(self.url)
            time.sleep(2)
            
            books = self.get_book_elements()
            book_title = None
            
            for book in books:
                try:
                    title_link = book.find_element(By.CSS_SELECTOR, ".rt-td:nth-child(2) span a")
                    book_title = title_link.text.strip()
                    if book_title:
                        title_link.click()
                        break
                except:
                    continue
            
            if not book_title:
                self.log_result(test_id, test_name, False, "Aucun livre cliquable trouvé")
                return
            
            time.sleep(2)
            current_url = self.driver.current_url
            
            if "book=" in current_url:
                try:
                    details_present = False
                    detail_selectors = [
                        (By.XPATH, "//*[contains(text(), 'ISBN')]"),
                        (By.XPATH, "//*[contains(text(), 'Publisher')]"),
                        (By.ID, "userName-value"),
                        (By.CSS_SELECTOR, ".text-right.fullButton"),
                        (By.XPATH, "//label[@id='userName-label']"),
                        (By.CSS_SELECTOR, "#title-wrapper")
                    ]
                    
                    for selector in detail_selectors:
                        elements = self.driver.find_elements(*selector)
                        if len(elements) > 0:
                            details_present = True
                            break
                    
                    if details_present:
                        self.log_result(test_id, test_name, True, f"Navigation réussie vers détails de '{book_title}'")
                    else:
                        self.log_result(test_id, test_name, False, "Page de détails mais éléments manquants")
                except:
                    self.log_result(test_id, test_name, False, "Impossible de vérifier les détails")
            else:
                self.log_result(test_id, test_name, False, "URL n'a pas changé correctement")
                
        except Exception as e:
            self.log_result(test_id, test_name, False, f"Erreur: {str(e)}")
            
    # ========================================================================
    # TEST CASE 04 - SQL INJECTION PROTECTION
    # ========================================================================
    def test_04_sql_injection_protection(self):
        """TC-004: Test SQL injection protection"""
        test_id = "TC-004"
        test_name = "Protection contre injection SQL"
        
        sql_patterns = [
            "' OR '1'='1",
            "'; DROP TABLE books; --",
            '" OR 1=1 --',
            "' UNION SELECT * FROM users --"
        ]
        
        try:
            all_safe = True
            
            for pattern in sql_patterns:
                self.driver.get(self.url)
                time.sleep(1)
                
                search_input = self.get_search_input()
                if not search_input:
                    all_safe = False
                    self.log_result(test_id, test_name, False, "Champ de recherche non trouvé")
                    return
                    
                search_input.send_keys(pattern)
                time.sleep(1)
                
                page_source = self.driver.page_source.lower()
                sql_errors = ["sql syntax", "mysql", "database error", "query failed", "ora-", "pg_"]
                has_sql_error = any(err in page_source for err in sql_errors)
                
                if has_sql_error:
                    all_safe = False
                    self.log_result(test_id, test_name, False, f"Erreur SQL détectée avec pattern: {pattern}")
                    break
            
            if all_safe:
                self.log_result(test_id, test_name, True, "Tous les patterns SQL sont correctement traités")
            
        except Exception as e:
            self.log_result(test_id, test_name, False, f"Erreur: {str(e)}")
            
    # ========================================================================
    # TEST CASE 05 - TITLE COLUMN SORTING
    # ========================================================================
    def test_05_title_column_sorting(self):
        """TC-005: Verify title column sorting"""
        test_id = "TC-005"
        test_name = "Tri de la colonne Title"
        
        try:
            self.driver.get(self.url)
            time.sleep(2)
            
            def get_titles():
                titles = []
                books = self.get_book_elements()
                for book in books:
                    try:
                        title = book.find_element(By.CSS_SELECTOR, ".rt-td:nth-child(2) span").text.strip()
                        if title:
                            titles.append(title)
                    except:
                        continue
                return titles
            
            initial_titles = get_titles()
            
            if len(initial_titles) < 2:
                self.log_result(test_id, test_name, False, "Pas assez de livres pour tester le tri")
                return
            
            try:
                title_header = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'rt-resizable-header') and contains(., 'Title')]"))
                )
                title_header.click()
                time.sleep(1.5)
                
                sorted_asc = get_titles()
                expected_asc = sorted(initial_titles, key=str.lower)
                
                title_header.click()
                time.sleep(1.5)
                
                sorted_desc = get_titles()
                expected_desc = sorted(initial_titles, key=str.lower, reverse=True)
                
                asc_correct = sorted_asc == expected_asc
                desc_correct = sorted_desc == expected_desc
                
                if asc_correct and desc_correct:
                    self.log_result(test_id, test_name, True, "Tri ascendant et descendant fonctionnent correctement")
                elif asc_correct:
                    self.log_result(test_id, test_name, False, "Tri ascendant OK mais tri descendant incorrect")
                elif desc_correct:
                    self.log_result(test_id, test_name, False, "Tri descendant OK mais tri ascendant incorrect")
                else:
                    self.log_result(test_id, test_name, False, "Tri ascendant et descendant incorrects")
                    
            except TimeoutException:
                self.log_result(test_id, test_name, False, "En-tête de colonne Title non trouvé ou non cliquable")
                
        except Exception as e:
            self.log_result(test_id, test_name, False, f"Erreur: {str(e)}")
            
    # ========================================================================
    # TEST SUMMARY & REPORTING
    # ========================================================================
    def print_summary(self):
        """Print test execution summary"""
        print("\n" + "="*70)
        print("📊 RÉSUMÉ DES TESTS")
        print("="*70)
        
        passed = sum(1 for r in self.results if "PASS" in r["status"])
        failed = sum(1 for r in self.results if "FAIL" in r["status"])
        total = len(self.results)
        
        for result in self.results:
            print(f"{result['status']} - {result['id']}: {result['name']}")
            
        print("="*70)
        print(f"Total: {total} | Réussis: {passed} | Échoués: {failed}")
        
        if total > 0:
            print(f"Taux de réussite: {(passed/total*100):.1f}%")
        
        if failed > 0:
            print(f"\n📁 Screenshots sauvegardés dans: {self.screenshot_dir}")
        
        print("="*70)
        
    # ========================================================================
    # TEST EXECUTION
    # ========================================================================
    def run_all_tests(self):
        """Execute all tests"""
        print("\n🚀 DÉMARRAGE DES TESTS AUTOMATISÉS - DemoQA Books")
        print("="*70)
        
        try:
            self.test_01_search_book_cover_consistency()
            self.test_02_case_insensitive_search()
            self.test_03_click_book_navigation()
            self.test_04_sql_injection_protection()
            self.test_05_title_column_sorting()
        except Exception as e:
            print(f"\n❌ Erreur fatale lors de l'exécution: {str(e)}")
        finally:
            self.print_summary()
            try:
                self.driver.quit()
            except:
                pass
            print("\n✨ Tests terminés\n")

if __name__ == "__main__":
    tester = DemoQABooksTests()
    tester.run_all_tests()
