Feature: The shopcart service back-end
    As a E-commerce Owner
    I need a RESTful shopcart service
    So that I can keep track of all my shopcarts

Background:
    Given the database loaded with dummy data

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

Scenario: Get a particular shopcart
  Given the following shopcarts
    | uid   | sid   | subtotal | product sku | product quantity | product name      | product unitprice |
    | 1     | 1     | 0.00     | 123456780   | 2                | Settlers of Catan | 27.99             |
    | 1     | 1     | 0.00     | 876543210   | 1                | Risk              | 27.99             |
    | 2     | 2     | 0.00     |             |                  |                   |                   |
    | 3     | 3     | 0.00     | 114672050   | 1                | Game of Life      | 13.99             |
  When I search for a shopcart with sid "3"
    | uid   | sid   | subtotal | product sku | product quantity | product name      | product unitprice |
    | 3     | 3     | 0.00     | 114672050   | 1                | Game of Life      | 13.99             |
  Then I should see shopcart with id "3"
  And I should see a product having sku "114672050", quantity "1", name "Game of Life" and unitprice "13.99 "
  And I should not see shopcart with id "1"
  And I should not see shopcart with id "2"

Scenario: Get a particular shopcart
  Given the following shopcarts
    | uid   | sid   | subtotal | product sku | product quantity | product name      | product unitprice |
    | 1     | 1     | 0.00     | 123456780   | 2                | Settlers of Catan | 27.99             |
    | 1     | 1     | 0.00     | 876543210   | 1                | Risk              | 27.99             |
    | 2     | 2     | 0.00     |             |                  |                   |                   |
    | 3     | 3     | 0.00     | 114672050   | 1                | Game of Life      | 13.99             |
  When I search for a shopcart with sid "13"
  Then I should see "Shopping Cart with id: 13 was not found"
  And I should not see shopcart with id "1"
  And I should not see shopcart with id "2"
  And I should not see shopcart with id "3"

Scenario: Get a particular product
  Given a shopcart with uid "3" exists
    | uid   | sid   | subtotal | product sku | product quantity | product name      | product unitprice |
    | 3     | 3     | 0.00     | 114672050   | 1                | Game of Life      | 13.99             |
  And a product with sku "114672050" exists
  When I search for a product with sku "114672050"
    | product sku | product quantity | product name      | product unitprice |
    | 114672050   | 1                | Game of Life      | 13.99             |
  Then I should see a product having sku "114672050", quantity "1", name "Game of Life" and unitprice "13.99"

Scenario: Get a particular product
  Given a shopcart with uid "3" exists
    | uid   | sid   | subtotal | product sku | product quantity | product name      | product unitprice |
    | 3     | 3     | 0.00     | 114672050   | 1                | Game of Life      | 13.99             |
  And a product with sku "114672154" does not exist
  When I search for a product with sku "114672154"
  Then I should see "Product with sku: 114672154 was not found in the cart for user"

Scenario: Get a particular product
  Given a shopcart with uid "13" does not exist
  When I search for a product with sku "114672050"
  Then I should see "Shopping Cart with id: 13 was not found"

Scenario: Get all the products of a shopcart
  Given a shopcart with uid "1" exists
    | uid   | sid   | subtotal | product sku | product quantity | product name      | product unitprice |
    | 1     | 1     | 0.00     | 123456780   | 2                | Settlers of Catan | 27.99             |
    | 1     | 1     | 0.00     | 876543210   | 1                | Risk              | 27.99             |
  When I fetch all the products of the shopcart
  Then I should see a product having sku "123456780", quantity "2", name "Settlers of Catan" and unitprice "27.99"
  And I should see a product having sku "876543210", quantity "1", name "Risk" and unitprice "27.99"

Scenario: Get all the products of a shopcart
  Given a shopcart with uid "2" exists
    | uid   | sid   | subtotal | product sku | product quantity | product name      | product unitprice |
    | 2     | 2     | 0.00     |             |                  |                   |                   |
  When I fetch all the products of the shopcart
  Then I should see "The cart contains no products"

Scenario: Get all the products of a shopcart
  Given a shopcart with uid "22" does not exist
  When I fetch all the products of the shopcart
  Then I should see "Shopping Cart with id: 22 was not found"

Scenario: Get all the products of a shopcart
  Given a shopcart with uid "1" exists
    | uid   | sid   | subtotal | product sku | product quantity | product name      | product unitprice |
    | 1     | 1     | 0.00     | 123456780   | 2                | Settlers of Catan | 27.99             |
    | 1     | 1     | 0.00     | 876543210   | 1                | Risk              | 27.99             |
  And a product with name "Risk" exists
  When I query the shopcart with product name "Risk"
  Then I should see a product having sku "876543210", quantity "1", name "Risk" and unitprice "27.99"

Scenario: Get all the products of a shopcart
  Given a shopcart with uid "1" exists
    | uid   | sid   | subtotal | product sku | product quantity | product name      | product unitprice |
    | 1     | 1     | 0.00     | 123456780   | 2                | Settlers of Catan | 27.99             |
    | 1     | 1     | 0.00     | 876543210   | 1                | Risk              | 27.99             |
  And a product with name "Monopoly" does not exist
  When I query the shopcart with product name "Monopoly"
  Then I should see "Product with name: Monopoly was not found"

Scenario: Get subtotal of a shopcart
  Given a shopcart with uid "1" exists
    | uid   | sid   | subtotal | product sku | product quantity | product name      | product unitprice |
    | 1     | 1     | 0.00     | 123456780   | 2                | Settlers of Catan | 27.99             |
    | 1     | 1     | 0.00     | 876543210   | 1                | Risk              | 27.99             |
  When I get subtotal for the shopcart
  Then I should see subtotal of "83.97" in the shopcart

Scenario: Get subtotal of a shopcart
  Given a shopcart with uid "15" does not exist
  When I get subtotal for the shopcart
  Then I should see "Shopping Cart with id: 15 was not found"

Scenario: Create a new product
  Given a shopcart with uid "2" exists
  When I load a new product with just sku "121987337", quantity "5", name "Carrom" in the shopcart
    | product sku | product quantity | product name |
    | 121987337   | 5                | Carrom       |
  Then I should see "Data is not valid"

Scenario: Create a new product
  Given a shopcart with uid "2" exists
  When I load a new product without any details in the shopcart
  Then I should see "Data is not valid"

Scenario: Create a new product
  Given a shopcart with uid "12" does not exist
  When I load a new product with sku "121987567", quantity "15", name "Charades", unitprice "4.99" in the shopcart
    | product sku | product quantity | product name | product unitprice |
    | 121987567   | 15               | Charades     | 4.99              |
  Then I should see "Shopping Cart with id: 12 was not found"

Scenario: Create a new product
  Given a shopcart with uid "2" exists
  When I load a new product with sku "121986367", quantity "100", name "Scattegories", unitprice "64.99" in the shopcart
    | product sku | product quantity | product name | product unitprice |
    | 121986367   | 100              | Scattegories | 64.99             |
  Then I should see a product having sku "121986367", quantity "100", name "Scattegories" and unitprice "64.99"

Scenario: List all shopcarts
    When I visit "shopcarts"
    Then I should see "Settlers of Catan"
    And I should see "Risk"
    And I should see "Game of Life"
    And I should see shopcart with id "1"
    And I should see shopcart with id "2"
    And I should see shopcart with id "3"

Scenario: Update a product
    Given a shopcart with uid "1" exists
    When I change a product with sku "123456780" to sku "123456781", quantity "3", name "Catan Expansion", and unitprice "22.99"
    Then I should see a product having sku "123456781", quantity "3", name "Catan Expansion" and unitprice "22.99"
    And I should not see a product with sku "123456780"

Scenario: Update a product
    Given a shopcart with uid "54" does not exist
    When I change a product with invalid sid or sku "123456780" to sku "123456781", quantity "3", name "Catan Expansion", and unitprice "22.99"
    Then I should see "Shopping Cart with id: 54 was not found"

Scenario: Update a product
    Given a shopcart with uid "1" exists
    When I change a product with invalid sid or sku "0" to sku "123456781", quantity "3", name "Catan Expansion", and unitprice "22.99"
    Then I should see "Product 0 was not found in shopping cart 1"

Scenario: Update a product
    Given a shopcart with uid "3" exists
    When I change a product with sku "114672050" to an empty product
    Then I should see "Product data is not valid"

Scenario: Delete a shopcart
    When I visit "shopcarts"
    Then I should see shopcart with id "1"
    And I should see shopcart with id "2"
    And I should see shopcart with id "3"
    When I delete "shopcarts" with id "3"
    And I search for a shopcart with sid "3"
    Then I should see "Shopping Cart with id: 3 was not found"

Scenario: Delete a product
    Given a shopcart with uid "1" exists
    When I search for a product with sku "876543210"
    Then I should see a product having sku "876543210", quantity "1", name "Risk" and unitprice "27.99"
    When I delete product with sku "876543210"
    And I search for a product with sku "876543210"
    Then I should see "Product with sku: 876543210 was not found in the cart for user"

Scenario: List all shopcarts under a particular user
    When I query "shopcarts" with query parameter uid "1"
    Then I should see shopcart with uid "1"
    And I should not see shopcart with uid "2"
    And I should not see shopcart with uid "3"