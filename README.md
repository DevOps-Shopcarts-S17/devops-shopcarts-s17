# devops-shopcarts-s17
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
Request | Link | Functionality     
------- | ---------------- | ----------:
GET  | / | Show Index page
GET  | /shopcarts        | List all shopcarts      
GET  | /shopcarts/{sid} | List a specific shopcart   
GET  | /shopcarts?uid={uid} | Query for a specific shopcart
GET  | /shopcarts/{sid}/products | List all products in a shopcart
GET  | /shopcarts/{sid}/products/{sku} | List a specific product in a shopcart
GET  | /shopcarts/{sid}/products?name={name} | Query for a specific product in a shopcart
POST | /shopcarts/{uid=4} | Create a new empty cart for a user
