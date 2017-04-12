# devops-shopcarts-s17

[![Build Status](https://travis-ci.org/DevOps-Shopcarts-S17/devops-shopcarts-s17.svg?branch=master)](https://travis-ci.org/DevOps-Shopcarts-S17/devops-shopcarts-s17)

This repo by Echo Squad is for the development of shopcarts which is a collection of products to buy.
# Usage
Please visit
* [Shopcart](http://nyu-shopcarts-service.mybluemix.net/) - Index page hosted on bluemix

## For local deployment
    $ git clone https://github.com/Pratik-Karnik/devops-shopcarts-s17
    $ cd devops-shopcarts-s17
    $ vagrant up
    $ vagrant ssh
    $ start_flask
  Then visit - [0.0.0.0/8888](0.0.0.0/8888)

## Authors
* **Pratik Parag Karnik** - [Pratik-Karnik](https://github.com/Pratik-Karnik)
* **Hongtao Cheng** - [senongtor](https://github.com/senongtor)
* **Wesley Painter** - [WesPainter](https://github.com/WesPainter)
* **Tejas Rao Chagarlamudi** - [trc311](https://github.com/trc311)

## Description
Request | Link | Functionality | Sample Content    
------- | :---------------- | :---------- | :----------
GET  | / | Show Index page
GET  | /shopcarts        | List all shopcarts      
GET  | /shopcarts/{sid} | List a specific shopcart   
GET  | /shopcarts?uid={uid} | Query for a specific shopcart
GET  | /shopcarts/{sid}/products | List all products in a shopcart
GET  | /shopcarts/{sid}/products/{sku} | List a specific product in a shopcart
GET  | /shopcarts/{sid}/products?name={name} | Query for a specific product in a shopcart
POST | /shopcarts/ | Create a new empty cart for a user | {"uid":4}
POST | /shopcarts/ | Create a new cart along with some products for a user | {"uid": 5,"products": [{"sku": 44982050,"quantity": 2,"name": "Scattegories","unitprice": 8.99}]}
POST | /shopcarts/{sid}/products | Add a new product to the cart | {"products": [{"sku": 218672050,"quantity": 12,"name": "Taboo","unitprice": 1.99}]}
PUT | /shopcarts/{sid}/products/{sku} | Update a product in the cart | {"products": [{"sku": 218672050,"quantity": 13,"name": "Taboo","unitprice": 3.99}]}
DELETE | /shopcarts/{sid} | Delete a shopcart
DELETE | /shopcarts/{sid}/products/{sku} | Delete a product in a cart
PUT | /shopcarts/{sid}/subtotal | ACTION: update subtotal of the cart
