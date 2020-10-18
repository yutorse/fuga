from flask import *  # 必要なライブラリのインポート
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String
from user import User, session
from scrape import log_in_check

app = Flask(__name__)  # アプリの設定
app.secret_key = "b'Q\x08\xe1Nb\\\x9c\xc0\xa1\xdaABC\x94\xd5\x15\x13\xb3t\x1c\xcf\xba\x18\x05'"

# @app.route("/")  # どのページで実行する関数か設定
# def main():
#     return "Hello, World!"  # Hello, World! を出力

#views
@app.route('/', methods=['GET', 'POST'])
def login_access():
    if request.method == 'GET':
        return render_template(
            'index.html'
        )
    if request.method == 'POST':
        id = request.form['id']

        #エラーチェック
        error_message = None
        if not id:
            error_message = 'IDの入力は必須です'

        user = session.query(User).filter(User.id == id).first()

        #ユーザー名ミス
        if user is None:
            error_message = 'ユーザー名が正しくありません'

        #エラーを表示
        if error_message is not None:
            flash(error_message, category = 'alert alert-danger')
            return redirect(url_for('login_access'))

        #エラーがなければログイン完了
        flash('{}さんとしてログインしました'.format(id), category = 'alert alert-info')
        #return redirect(url_for('view_home'))
        return redirect(url_for('view_home', id = id))


@app.route('/signup', methods=['GET', 'POST'])
def signup_access():
    if request.method == 'GET':
        return render_template(
            'signup.html'
        )
    if request.method == 'POST':
        id = request.form['id']
        password = request.form['password']

        #エラーチェック
        error_message = None
        if not id:
            error_message = 'IDの入力は必須です'
        elif not password:
            error_message = 'パスワードの入力は必須です'
        #重複をチェック
        existing_id = session.query(User).get(id)
        if existing_id:
            error_message = 'このIDはすでに登録されています'
        #ログインできるかチェック
        if not log_in_check(id, password):
            error_message = 'PandAにログインできませんでした'

        #エラーを表示
        if error_message is not None:
            flash(error_message, category = 'alert alert-danger')
            return redirect (url_for('signup_access'))

        #エラーがなければ登録
        user = User(id, password)
        session.add(user)
        session.commit()

        flash('登録が完了しました。ログインしてください。', category = 'alert alert-info')
        return redirect(url_for('login_access'))

@app.route('/logout')
def logout():
    """ログアウトする"""
    flash('ログアウトしました', category='alert alert-info')
    return redirect(url_for('login_access'))

@app.route('/home')
def view_home():
    user_id = request.args.get("id", "")
    print(user_id)
    return render_template('home.html', id=user_id)

if __name__ == "__main__":  # 実行されたら
    app.run(debug=False)  # デバッグモード、localhost:8888 で スレッドオンで実行