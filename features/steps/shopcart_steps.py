from behave import *
import json
import shopcart as server

# Status Codes
HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_204_NO_CONTENT = 204
HTTP_400_BAD_REQUEST = 400
HTTP_404_NOT_FOUND = 404
HTTP_409_CONFLICT = 409

@when(u'I visit the "home page"')
def step_impl(context):
	context.resp = context.app.get('/')

@then(u'I should see "{message}"')
def step_impl(context, message):
	assert message in context.resp.data

@then(u'I should not see "{message}"')
def step_impl(context, message):
	assert message not in context.resp.data

@when(u'I create a new shopcart for uid "{uid}"')
def step_impl(context,uid):
	new_shopcart = { "uid": int(uid)}
	data = json.dumps(new_shopcart)
	context.resp = context.app.post('/shopcarts', data=data, content_type='application/json')

@when(u'I create a new shopcart without a uid')
def step_impl(context):
	new_shopcart = {}
	data = json.dumps(new_shopcart)
	context.resp = context.app.post('/shopcarts', data=data, content_type='application/json')

@when(u'I create a new shopcart with uid "{id}" having a product with sku "{sku}", quantity "{quantity}", name "{name}" and unitprice "{unitprice}"')
def step_impl(context,id,sku,quantity,name,unitprice):
	new_shopcart = { "uid": int(id), "products": [{"sku" : int(sku), "quantity" : int(quantity), "name" : name , "unitprice" : float(unitprice)}] }
	data = json.dumps(new_shopcart)
	context.resp = context.app.post('/shopcarts', data=data, content_type='application/json')

@then(u'I should see a new shopcart with uid "{id}"')
def step_impl(context,id):
	new_json = json.loads(context.resp.data)
	assert context.resp.status_code == HTTP_201_CREATED
	assert int(new_json['uid']) == int(id)

@then(u'I should see a product having sku "{sku}", quantity "{quantity}", name "{name}" and unitprice "{unitprice}"')
def step_impl(context,sku,quantity,name,unitprice):
	new_json = json.loads(context.resp.data)

	if hasattr(context,'get_product'):
		assert context.resp.status_code == 200
		if new_json['sku'] == int(sku):
			assert new_json['quantity'] == int(quantity)
			assert new_json['name'] == name
			assert new_json['unitprice'] == float(unitprice)
	else:
		for i in range(0,len(new_json['products'])):
			if new_json['products'][i]['sku'] == int(sku):
				assert new_json['products'][i]['quantity'] == int(quantity)
				assert new_json['products'][i]['name'] == name
				assert new_json['products'][i]['unitprice'] == float(unitprice)

@then(u'I should not see a product with sku "{sku}"')
def step_impl(context,sku):
	data = json.loads(context.resp.data)
	for i in range(0,len(data['products'])):
		if data['products'][0]['sku'] == int(sku):
			assert False
	assert True

@given(u'the following shopcarts')
def step_impl(context):
	context.resp = context.app.get('/shopcarts')
	assert context.resp.status_code == 200

@when(u'I search for a shopcart with sid "{id}"')
def step_impl(context,id):
	context.resp = context.app.get('/shopcarts/'+id)
	context.get_shopcart = True

@when(u'I search for a product with sku "{sku}"')
def step_impl(context,sku):
    context.resp = context.app.get('/shopcarts/'+context.current_shopcart+'/products/'+sku)
    context.get_product = True

@given(u'a shopcart with uid "{id}" exists')
def step_impl(context,id):
	context.resp = context.app.get('/shopcarts/'+id)
	context.current_shopcart = id
	assert context.resp.status_code == 200

@given(u'a shopcart with uid "{id}" does not exist')
def step_impl(context,id):
	context.resp = context.app.get('/shopcarts/'+id)
	context.current_shopcart = id
	assert context.resp.status_code == 404

@given(u'a product with sku "{sku}" exists')
def step_impl(context,sku):
    context.resp = context.app.get('/shopcarts/'+context.current_shopcart+'/products/'+sku)
    assert context.resp.status_code == 200

@given(u'a product with sku "{sku}" does not exist')
def step_impl(context,sku):
    context.resp = context.app.get('/shopcarts/'+context.current_shopcart+'/products/'+sku)
    assert context.resp.status_code == 404

@when(u'I get subtotal for the shopcart')
def step_impl(context):
	context.resp = context.app.put('/shopcarts/'+context.current_shopcart+'/subtotal')

@then(u'I should see subtotal of "{subtotal}" in the shopcart')
def step_impl(context, subtotal):
    data = json.loads(context.resp.data)
    assert context.resp.status_code == 200
    assert data['subtotal'] == float(subtotal)

@when(u'I load a new product without any details in the shopcart')
def step_impl(context):
	new_product = {}
	data = json.dumps(new_product)
	url = '/shopcarts/'+context.current_shopcart+'/products'
	context.resp = context.app.post(url, data=data, content_type='application/json')

@when(u'I load a new product with just sku "{sku}", quantity "{quantity}", name "{name}" in the shopcart')
def step_impl(context,sku,quantity,name):
	new_product = { "products": [{"sku" : int(sku), "quantity" : int(quantity), "name" : name}] }
	data = json.dumps(new_product)
	url = '/shopcarts/'+context.current_shopcart+'/products'
	context.resp = context.app.post(url, data=data, content_type='application/json')

@when(u'I load a new product with sku "{sku}", quantity "{quantity}", name "{name}", unitprice "{unitprice}" in the shopcart')
def step_impl(context,sku,quantity,name,unitprice):
	new_product = { "products": [{"sku" : int(sku), "quantity" : int(quantity), "name" : name, "unitprice" : float(unitprice)}] }
	data = json.dumps(new_product)
	url = '/shopcarts/'+context.current_shopcart+'/products'
	context.resp = context.app.post(url, data=data, content_type='application/json')

@then(u'I should see shopcart with id "{id}"')
def step_impl(context, id):
	data = json.loads(context.resp.data)
	found_id = False

	if hasattr(context,'get_shopcart'):
		assert context.resp.status_code == 200
		if data['sid'] == int(id):
			found_id = True
	else:
		for cart in data:
			if cart["sid"] == int(id):
				found_id = True
	assert found_id

@then(u'I should not see shopcart with id "{id}"')
def step_impl(context,id):
    data = json.loads(context.resp.data)
    if 'sid' in data:
        assert int(data['sid']) != int(id)
    else:
        assert context.resp.status_code == 404

@when(u'I visit "{url}"')
def step_impl(context, url):
    context.resp = context.app.get(url)
    assert context.resp.status_code == 200

@when(u'I change a product with sku "{sku_original}" to sku "{sku_new}", quantity "{quantity}", name "{name}", and unitprice "{unitprice}"')
def step_impl(context,sku_original, sku_new, quantity, name, unitprice):
	new_product = { "products": [{"sku" : int(sku_new), "quantity" : int(quantity), "name" : name, "unitprice" : float(unitprice)}] }
	data = json.dumps(new_product)
	url = '/shopcarts/'+context.current_shopcart+'/products/' + sku_original
	context.resp = context.app.put(url, data=data, content_type='application/json')
	assert context.resp.status_code == 200

@when(u'I change a product with invalid sid or sku "{sku_original}" to sku "{sku_new}", quantity "{quantity}", name "{name}", and unitprice "{unitprice}"')
def step_impl(context,sku_original, sku_new, quantity, name, unitprice):
	new_product = { "products": [{"sku" : int(sku_new), "quantity" : int(quantity), "name" : name, "unitprice" : float(unitprice)}] }
	data = json.dumps(new_product)
	url = '/shopcarts/'+context.current_shopcart+'/products/' + sku_original
	context.resp = context.app.put(url, data=data, content_type='application/json')
	assert context.resp.status_code == 404

@when(u'I change a product with sku "{sku}" to an empty product')
def step_impl(context,sku):
	new_product = { "products": [{}] }
	data = json.dumps(new_product)
	url = '/shopcarts/'+context.current_shopcart+'/products/' + sku
	context.resp = context.app.put(url, data=data, content_type='application/json')
	assert context.resp.status_code == 400

@when(u'I delete "{url}" with id "{id}"')
def step_impl(context, url, id):
    target_url = '/{}/{}'.format(url, id)
    context.resp = context.app.delete(target_url)
    assert context.resp.status_code == 204
    assert context.resp.data is ""

@when(u'I delete product with sku "{sku}"')
def step_impl(context, sku):
    context.resp = context.app.delete('/shopcarts/'+context.current_shopcart+'/products/'+sku)
    assert context.resp.status_code == 204

@when(u'I query "{url}" with query parameter uid "{uid}"')
def step_impl(context, url, uid):
    target_url = '/{}?uid={}'.format(url, uid)
    context.resp = context.app.get(target_url)
    assert context.resp.status_code == 200

@then(u'I should see shopcart with uid "{uid}"')
def step_impl(context, uid):
    data = json.loads(context.resp.data)
    assert int(data['uid']) == int(uid)

@then(u'I should not see shopcart with uid "{uid}"')
def step_impl(context, uid):
    data = json.loads(context.resp.data)
    assert int(data['uid']) != int(uid)
