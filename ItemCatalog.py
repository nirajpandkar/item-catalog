from flask import Flask, render_template, request, redirect, url_for
from database import Base, Category, Item
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

app = Flask(__name__)

engine = create_engine('sqlite:///categories.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/')
@app.route('/categories')
def show_categories():
    categories = session.query(Category).all()
    return render_template("categories.html", categories=categories)


@app.route('/category/new', methods=['GET', 'POST'])
def new_category():
    '''
        Creates a new category
    '''
    if request.method == 'POST':
        genre = Category(name=request.form['new_category'])
        session.add(genre)
        session.commit()
        return redirect(url_for('show_categories'))
    else:
        return render_template("newcategory.html")


@app.route('/category/<string:category_name>/edit', methods=['GET', 'POST'])
def edit_category(category_name):
    '''
        Arguments: Name of the category which is to be edited

        Edits an existing category name.
    '''
    edited_genre = session.query(Category).filter_by(name=category_name)\
        .one()
    if request.method == 'POST':
        if request.form['edit_category']:
            edited_genre.name = request.form['edit_category']
        session.add(edited_genre)
        session.commit()
        return redirect(url_for('show_categories'))
    else:
        return render_template("editcategory.html", genre=edited_genre.name)


@app.route('/category/<string:category_name>/delete', methods=['GET', 'POST'])
def delete_category(category_name):
    '''
        Arguments: Name of the category which is to be edited

        Deletes an existing category name.
    '''
    deleted_genre = session.query(Category).filter_by(name=category_name)
    if request.method == 'POST':
        deleted_genre.delete(synchronize_session=False)
        session.commit()
        return redirect(url_for('show_categories'))
    else:
        return render_template("deletecategory.html",
                               genre=deleted_genre.one().name)


@app.route('/category/<string:name>/items')
@app.route('/category/<string:name>/')
def show_items(name):
    books = session.query(Item).filter_by(category_name=name)
    return render_template("items.html", books=books)

# @app.route('/category/<string:cateogry_name>/<string:item_name>')
# def show_particular_item(category_name, item_name):
#
#     return render_template("item.html")


@app.route('/category/category_name/item/new')
def new_item():
    return render_template("newitem.html")


@app.route('/category/category_name/item/item_name/edit')
def edit_items():
    return render_template("edititem.html")


@app.route('/category/category_name/item/item_name/delete')
def delete_items():
    return render_template("deleteitem.html")

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
