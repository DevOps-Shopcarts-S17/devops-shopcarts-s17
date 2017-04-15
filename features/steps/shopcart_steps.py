from behave import *
import json
import shopcart as server

@when(u'I visit the "home page"')
def step_impl(context):
    context.resp = context.app.get('/')

@then(u'I should see "{message}"')
def step_impl(context, message):
    assert message in context.resp.data

@then(u'I should not see "{message}"')
def step_impl(context, message):
    assert message not in context.resp.data

@when(u'I visit "{url}"')
def step_impl(context, url):
    context.resp = context.app.get(url)
    assert context.resp.status_code == 200

@when(u'I search shopcarts with uid "{uid}"')
def step_impl(context, uid):
    context.resp = context.app.get('shopcarts?uid='+uid)
    assert context.resp.status_code == 200
