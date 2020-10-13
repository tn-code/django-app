私的な情報を横断的に整理するための統合アプリケーション。

Python製フレームワークのDjangoをベースに、Vue.jsをテンプレート内に取り込んだインタラクティブなページも実装。

外部APIの利用やRedisによるキャッシュの活用のほか、
matplotlibを用いたグラフ描画でデータの可視化も実現。

個人的な活用のため、開発用のローカルサーバーでのみの運用を想定。

### 開発環境

|  ツール  |  バージョン  |
| ---- | ---- |
|  Python  |  3.7.3  |
|  Django  |  2.2.7  |
|  Vue.js  |  2.2.7  |
|  Redis  |  3.2.100  |
|  Bootstrap  |  4.4.1  |
|  jQuery  |  3.4.1  |
|  SQLite  |  3.11.2  |
|  matplotlib |  3.1.2  |

### 主な機能

|  機能  |  アプリ名  |
| ---- | ---- |
|  外国語学習支援  |  en, es  |
|  スケジュール管理/ToDoリスト  | utility  |
|  美術&デザイン管理  |  arts, atelier  |
|  読書記録管理  |  lib  |
|  医薬品データベース  |  pharmacy  |
|  料理レシピ管理  |  cuisine  |
|  楽曲チャート  |  music  |
|  国内外ニュース閲覧 |  news |
|  ブログ・日記 | blog |


### 主な習得事項

|  名前  |  ソース1  | ソース2 | ソース3 |
| ---- | ---- | ---- | ---- |
|  キャッシング(Redis)  |  music/views.py  | news/views.py | ---- |
|  Vue.js  |  templates/en/quizzes.html | en/views.py | ---- |
|  再帰関数  | pharmacy/views.py  | ---- | ---- |
|  グラフ描画(matplotlib)  |  en/views.py  | music/views.py | lib/views.py |
|  API活用  |  music/views.py  | news/views.py | blog/views.py |


####  スクリーンショット


#### matplotlibによるグラフ描画例



※ 掲載されているスクリーンショット内の画像及びアイコンは、一部を除いてのフリー素材配布サイトのものを利用しております。
