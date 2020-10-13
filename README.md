## 概要

私的な情報を横断的に整理するための統合アプリケーション。

Python製フレームワークのDjangoをベースに、Vue.jsをテンプレート内に取り込んだインタラクティブなページも実装。

外部APIの利用やRedisによるキャッシュの活用のほか、
matplotlibを用いたグラフ描画でデータの可視化も実現。

個人的な活用のため、開発用のローカルサーバーでのみの運用を想定。

## 開発環境

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

## 主な機能

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


## 主な習得事項

|  名前  |  ソース1  | ソース2 | ソース3 |
| ---- | ---- | ---- | ---- |
|  キャッシング(Redis)  |  music/views.py  | news/views.py | ---- |
|  Vue.js  |  templates/en/quizzes.html | en/views.py | ---- |
|  再帰関数  | pharmacy/views.py  | ---- | ---- |
|  グラフ描画(matplotlib)  |  en/views.py  | music/views.py | lib/views.py |
|  API活用  |  music/views.py  | news/views.py | blog/views.py |


##  スクリーンショット

### en
![en](https://user-images.githubusercontent.com/72479111/95816572-66eda480-0d5a-11eb-9669-ec26db7cb3e9.jpg)

![en2](https://user-images.githubusercontent.com/72479111/95816576-681ed180-0d5a-11eb-99ba-39e362ac91ed.jpg)

### cuisine
![cuisine2](https://user-images.githubusercontent.com/72479111/95816564-635a1d80-0d5a-11eb-980a-315dd81d3ba9.jpg)

![cuisine](https://user-images.githubusercontent.com/72479111/95816570-6523e100-0d5a-11eb-8a2a-1408942bd93a.jpg)

### pharmacy
![pharmacy](https://user-images.githubusercontent.com/72479111/95816563-6228f080-0d5a-11eb-96c3-978d70b39935.jpg)



#### matplotlibによるグラフ描画例

![mpl2](https://user-images.githubusercontent.com/72479111/95816558-605f2d00-0d5a-11eb-9c0f-e5f0afc24e42.jpg)

![mpl](https://user-images.githubusercontent.com/72479111/95816557-5dfcd300-0d5a-11eb-90be-963bc0d8963f.jpg)

![mpl3](https://user-images.githubusercontent.com/72479111/95816562-61905a00-0d5a-11eb-9839-14cda2c75fae.jpg)

※ 掲載されているスクリーンショット内の画像及びアイコンは、一部を除いてのフリー素材配布サイトのものを利用しております。
