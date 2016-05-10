import os
import sys
from datetime import datetime

import xmltodict
from jinja2 import FileSystemLoader, Environment

from models import *
from config import *


def test():
    name = "/Users/sonnt/Projects/xml_2_pdf/ranking2/154_2015-07-27.xml"
    f = open(name, "r")
    xml = xmltodict.parse(f)
    f.close()

    print xml['root']['distributor']['@id']
    for k,v in xml['root']['product'][3].items():
        print k, v
        if k == 'productPriceSupplier':
            for x in v['supplier']:
                for y, z in x.items():
                        print "-------", y, z


def get_basename(path):
    bname = os.path.basename(path)
    basename = os.path.splitext(bname)[0]
    return basename


def get_min(sellers):
    """
    Returns seller with lowest price
    :param sellers: List of sellers
    :return: Seller with lowest price
    """
    result = sellers[0]
    for seller in sellers[1:]:
        if float(result['#text']) > float(seller['#text']):
            result = seller

    return result


def generate_data(xml_file):
    f = open(xml_file, 'r')
    xml = xmltodict.parse(f)
    f.close()

    data = {}

    distributor_code = xml['root']['distributor']['@id']
    stats = {}
    stats['distributor_code'] = distributor_code
    stats['total'] = len(xml['root']['product'])
    stats['all_prod_pos1'] = stats['all_prod_pos2'] = stats['all_prod_pos3'] = 0
    stats['pre_brand_pos1'] = stats['pre_brand_pos2'] = stats['pre_brand_pos3'] = 0
    stats['bud_brand_pos1'] = stats['bud_brand_pos2'] = stats['bud_brand_pos3'] = 0
    stats['b2c_less'] = stats['b2c_more'] = stats['b2c_matching'] = 0
    stats['b2c_less_prods'] = []
    stats['b2c_more_prods'] = []
    stats['b2c_matching_prods'] = []
    stats['b2c_pre_less'] = stats['b2c_pre_more'] = stats['b2c_pre_matching'] = 0
    stats['b2c_pre_less_prods'] = []
    stats['b2c_pre_more_prods'] = []
    stats['b2c_pre_matching_prods'] = []
    stats['b2c_bud_less'] = stats['b2c_bud_more'] = stats['b2c_bud_matching'] = 0
    stats['b2c_bud_less_prods'] = []
    stats['b2c_bud_more_prods'] = []
    stats['b2c_bud_matching_prods'] = []

    brands = PREMIUM_BRANDS + BUDGET_BRANDS
    for br in brands:
        brand = Brand(name=br, distributor_code=distributor_code)
        data[br] = brand

    for product in xml['root']['product']:
        prod = Product()
        prod.distributor_code = distributor_code

        brand = product['brand']
        prod.brand = brand
        if not data.has_key(brand):
            data[brand] = Brand(name=brand, distributor_code=distributor_code)

        prod.ean = product['ean']
        prod.label = product['label']
        prod.ipc = product['ipc']
        prod.price = product['productPrice']
        price_suppliers = product['productPriceSupplier']
        if price_suppliers.has_key('supplier'):
            suppliers = price_suppliers['supplier']
            if isinstance(suppliers, dict):
                prod.suppliers.append(Seller(name=suppliers['@name'], price=suppliers['#text']))
                if suppliers['@id'] == distributor_code:
                    prod.position = "1/1"
                    data[brand].position1 += 1
                    stats['all_prod_pos1'] += 1
                    if brand in PREMIUM_BRANDS:
                        stats['pre_brand_pos1'] += 1
                    if brand in BUDGET_BRANDS:
                        stats['bud_brand_pos1'] += 1
            else:
                index = 1
                position = 0
                for sup in suppliers:
                    prod.suppliers.append(Seller(name=sup['@name'], price=sup['#text']))
                    if sup['@id'] == distributor_code:
                        position = index
                        if index in (1, 2, 3):
                            data[brand]['position%s' %index] += 1
                            stats['all_prod_pos%s' %index] += 1
                            if brand in PREMIUM_BRANDS:
                                stats['pre_brand_pos%s' %index] += 1
                            if brand in BUDGET_BRANDS:
                                stats['bud_brand_pos%s' %index] += 1
                    index += 1
                prod.position = "%s/%s" % (position, index - 1)
        if price_suppliers.has_key('sellerB2C'):
            sellers = price_suppliers['sellerB2C']
            if isinstance(sellers, dict):
                prod.sellers.append(Seller(name=sellers['@name'], price=sellers['#text']))
                best = sellers
            else:
                for sel in sellers:
                    prod.sellers.append(Seller(name=sel['@name'], price=sel['#text']))
                best = get_min(sellers)

            prod.best_seller_price = best['#text']
            prod.best_seller = best['@name']
            # if float(best['#text']) == float(prod.price):
            prod.bc_matching = True
            stats['b2c_matching'] += 1
            stats['b2c_matching_prods'].append(prod)
            if brand in PREMIUM_BRANDS:
                stats['b2c_pre_matching'] += 1
                stats['b2c_pre_matching_prods'].append(prod)
            if brand in BUDGET_BRANDS:
                stats['b2c_bud_matching'] += 1
                stats['b2c_bud_matching_prods'].append(prod)

            if float(best['#text']) < float(prod.price):
                prod.bc_more_exp = True
                stats['b2c_more'] += 1
                stats['b2c_more_prods'].append(prod)
                if brand in PREMIUM_BRANDS:
                    stats['b2c_pre_more'] += 1
                    stats['b2c_pre_more_prods'].append(prod)
                if brand in BUDGET_BRANDS:
                    stats['b2c_bud_more'] += 1
                    stats['b2c_bud_more_prods'].append(prod)
            else:
                prod.bc_less_exp = True
                stats['b2c_less'] += 1
                stats['b2c_less_prods'].append(prod)
                if brand in PREMIUM_BRANDS:
                    stats['b2c_pre_less'] += 1
                    stats['b2c_pre_less_prods'].append(prod)
                if brand in BUDGET_BRANDS:
                    stats['b2c_bud_less'] += 1
                    stats['b2c_bud_less_prods'].append(prod)
        data[brand].products.append(prod)

    for key, value in stats.items():
        if "_pos" in key:
            stats[key] = round(value*100/float(stats['total']), 2)

    return data, stats

#print generate_data("/Users/sonnt/Projects/xml_2_pdf/ranking2/154_2015-07-27.xml").keys()

def generate_html(xml_file):
    brands, stats = generate_data(xml_file)
    env = Environment(loader=FileSystemLoader("templates"))
    report_temp = env.get_template("report_template.html")
    prod_temp = env.get_template("product_listing_template.html")
    base_ctx = {
        'bootstrap_css_url': "https://maxcdn.bootstrapcdn.com/bootstrap/3.3.5/css/bootstrap.min.css", #"file://" + STATIC_ROOT + 'css/bootstrap.mim.css',
        'bootstrap_theme_css_url': "https://maxcdn.bootstrapcdn.com/bootstrap/3.3.5/css/bootstrap-theme.min.css", #"file://" + STATIC_ROOT + 'css/bootstrap-theme.mim.css',
        'logo_url': 'https://d3s763n0ugqswt.cloudfront.net/img/logo.png',
        'jquery_url': "https://ajax.googleapis.com/ajax/libs/jquery/1.11.3/jquery.min.js", #STATIC_ROOT + 'js/jquery-1.11.1.min.js',
        'bootstrap_js_url': "https://maxcdn.bootstrapcdn.com/bootstrap/3.3.5/js/bootstrap.min.js", #STATIC_ROOT + 'js/bootstrap.min.js',
    }

    pre_brands = []
    bud_brans = []
    all_prods = []
    pre_prods = []
    bud_prods = []
    for key, value in brands.items():
        total = len(value.products)
        if total != 0:
            value['position1'] = round(value['position1']* 100/float(total), 2)
            value['position2'] = round(value['position2']* 100/float(total), 2)
            value['position3'] = round(value['position3']* 100/float(total), 2)

        if key in PREMIUM_BRANDS:
            pre_brands.append(value)
            pre_prods += value.products
        if key in BUDGET_BRANDS:
            bud_brans.append(value)
            bud_prods += value.products
        all_prods += value.products

    ctx = stats.copy()
    ctx['pre_brands'] = pre_brands
    ctx['bud_brands'] = bud_brans
    current_date = datetime.now().strftime("%d-%m-%Y %H:%M")
    ctx['current_date']  = current_date
    ctx.update(base_ctx)

    bname = get_basename(xml_file)
    name = OUTPUT_PATH + '/' + bname + '_report.html'

    results = []
    all_ctx = {'products': all_prods,
               'id': 'all_prods',
               'title': 'ALL PRODUCTS'}
    results.append(all_ctx)

    pre_ctx = {'products': pre_prods,
               'id': 'pre_prods',
               'title': 'PREMIUM BRAND PRODUCTS'}
    results.append(pre_ctx)

    bud_ctx = {'products': bud_prods,
               'id': 'bud_prods',
               'title': 'BUDGET BRAND PRODUCTS'}
    results.append(bud_ctx)

    for br in PREMIUM_BRANDS + BUDGET_BRANDS:
        brand = brands[br]
        br_ctx = {'title': br,
              'id': br,
               'products': brand.products}
        results.append(br_ctx)

    results.append({
        'title': "Products are less expensive than Sellers B2C",
        'id': 'b2c_less_prods',
        'products': stats['b2c_less_prods']
    })
    results.append({
        'title': "Products are less expensive than Sellers B2C - PREMIUM BRANDS",
        'id': 'b2c_pre_less_prods',
        'products': stats['b2c_pre_less_prods']
    })
    results.append({
        'title': "Products are less expensive than Sellers B2C - BUDGET BRANDS",
        'id': 'b2c_bud_less_prods',
        'products': stats['b2c_bud_less_prods']
    })
    results.append({
        'title': "Products are more expensive than Sellers B2C",
        'id': 'b2c_more_prods',
        'products': stats['b2c_more_prods']
    })
    results.append({
        'title': "Products are more expensive than Sellers B2C - PREMIUM BRANDS",
        'id': 'b2c_pre_more_prods',
        'products': stats['b2c_pre_more_prods']
    })
    results.append({
        'title': "Products are more expensive than Sellers B2C - BUDGET BRANDS",
        'id': 'b2c_bud_more_prods',
        'products': stats['b2c_bud_more_prods']
    })
    results.append({
        'title': "Products are matching Sellers B2C",
        'id': 'b2c_matching_prods',
        'products': stats['b2c_matching_prods']
    })
    results.append({
        'title': "Products are matching Sellers B2C - PREMIUM BRANDS",
        'id': 'b2c_pre_matching_prods',
        'products': stats['b2c_pre_matching_prods']
    })
    results.append({
        'title': "Products are matching Sellers B2C - BUDGET BRANDS",
        'id': 'b2c_bud_matching_prods',
        'products': stats['b2c_bud_matching_prods']
    })

    ctx['results'] = results
    report_html = report_temp.render(**ctx)
    f = open(name, 'w+')
    f.write(report_html.encode('utf8'))
    f.close()
    return name

generate_html("174_2015-08-03-15h05.xml")
# if __name__ == '__main__':
#     print ("RUNNING: %s" % ' '.join(sys.argv))
#     if len(sys.argv) > 1:
#         xml = sys.argv[1]
#         print "Start generating data from file: ", xml
#         try:
#             out = generate_html(xml)
#             print "Generated successfully. All output are in %s" % out
#         except:
#             import traceback
#             print traceback.format_exc()
#             print "Invalid XML file"
#     else:
#         print "Please provide XML file"

