import sqlite3
from datetime import datetime

def get_post_ids():
    data = list(sqlite3.connect('form_data.db').cursor().execute('SELECT * FROM form'))
    return [i[-3] for i in data]

def get_posts(the_id = None):
    data = list(sqlite3.connect('form_data.db').cursor().execute('SELECT * FROM form'))
    if not the_id:
        return sorted(data, key=lambda x:datetime.strptime(x[-2], "%Y-%m-%d %H:%M:%S"), reverse=True)
    return sorted([i for i in data if i[-3] == the_id], key=lambda x:datetime.strptime(x[-2], "%Y-%m-%d %H:%M:%S"), reverse=True)


def add_post(**kwargs):
    headers = ['title', 'content', 'tags', 'email', 'id', 'date', 'isop']
    conn = sqlite3.connect('form_data.db')
    conn.execute('INSERT INTO form (title, content, tags, email, id, date, isop) VALUES (?, ?, ?, ?, ?, ?, ?)', tuple(kwargs[i] for i in headers))
    conn.commit()
    conn.close()

def update_views(question_id, viewer = None):

    if not isinstance(question_id, int):
        raise TypeError("question id must be an integer")
    """table name:questions, rows:(id int, viewers text (comma separated))"""
    #IDEA: could raise error if question_id not found, however, that would cause the site to crash
    original_listing = list(sqlite3.connect('question_data.db').cursor().execute('SELECT * FROM questions'))
    if not any(a == question_id for a, b in original_listing):
        conn = sqlite3.connect('question_data.db')
        conn.execute('INSERT INTO questions (id, viewers) VALUES (?, ?)', (question_id, '-------' if not viewer else viewer,))
        conn.commit()
        conn.close()
    else:
        current_listing = [i for i in original_listing if i[0] == question_id][0]
        #will need to add feature that checks if the viewer has already seen the post
        if viewer not in current_listing[-1]:
            print "in here"
            new_users = "{},{}".format(current_listing[-1], '-------' if not viewer else viewer)
            conn = sqlite3.connect('question_data.db')
            conn.execute('UPDATE questions SET viewers=? WHERE id = ?', (new_users, question_id,))
            conn.commit()
            conn.close()

def get_view_number(question_id):
    if not isinstance(question_id, int):
        raise TypeError("question id must be an integer")
    try:
        data = list(sqlite3.connect('question_data.db').cursor().execute('SELECT * FROM questions'))
        question = [b for a, b in data if a == question_id][0]
        return len(question.split(','))
    except:
        return 0
def add_user(email):
    conn = sqlite3.connect('formsprofiles.db')
    conn.execute('INSERT INTO formusers (email, summary, hasphoto) values (?, ?, ?)', (email, '', 0,))
    conn.commit()
    conn.close()

def update_user_form_details(email, **kwargs):
    #print tuple([kwargs.get(i, 0 if i == "photo" else '') for i in ['summary', 'photo']]+[email])
    conn = sqlite3.connect('formsprofiles.db')
    conn.execute('UPDATE formusers SET summary = ?, hasphoto = ? WHERE email = ?', tuple([kwargs.get(i, 0 if i == "photo" else '') for i in ['summary', 'photo']]+[email]))
    conn.commit()
    conn.close()

def get_user_form_listing(email):
    """table name:formusers, filename:formsprofiles.db, (email text, summary text, hasphoto int)"""
    return [i for i in list(sqlite3.connect('formsprofiles.db').cursor().execute('SELECT * FROM formusers')) if i[0] == email][0]
