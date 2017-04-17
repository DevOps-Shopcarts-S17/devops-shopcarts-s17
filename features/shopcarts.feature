Feature: The shopcart service back-end
    As a E-commerce Owner
    I need a RESTful shopcart service
    So that I can keep track of all my shopcarts

Scenario: The server is running
    When I visit the "home page"
    Then I should see "Shopcart Demo REST API Service"
    Then I should not see "404 Not Found"

Scenario: Create a new shopcart
  When I create a new shopcart for uid "6"
    | uid   |
    | 6     |
  Then I should see a new shopcart with uid "6"

Scenario: Create a new shopcart
  When I create a new shopcart for uid "1"
    | uid   |
    | 1     |
  Then I should see "Shopping Cart for uid 1 already exists"

Scenario: Create a new shopcart
  When I create a new shopcart without a uid
  Then I should see "Data is not valid"

Scenario: Create a new shopcart
  When I create a new shopcart with uid "7" having a product with sku "119873437", quantity "55", name "Lego" and unitprice "100"
    | uid   | product sku | product quantity | product name | product unitprice |
    | 7     | 119873437   | 55               | Lego         | 100               |
  Then I should see a new shopcart with uid "7"
  And I should see a product having sku "119873437", quantity "55", name "Lego" and unitprice "100"

Scenario: List all shopcarts
    When I visit "shopcarts"
    Then I should see "Settlers of Catan"
    And I should see "Risk"
    And I should see "Game of Life"
    And I should see shopcart with id "1"
    And I should see shopcart with id "2"
    And I should see shopcart with id "3"
