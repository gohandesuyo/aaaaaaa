# title: Pyxel Jump
# author: Takashi Kitao
# desc: A Pyxel simple game example
# site: https://github.com/kitao/pyxel
# license: MIT
# version: 1.0
# Usage: pyxel run FileName.py

import pyxel


class App:
    def __init__(self):
        pyxel.init(160, 120, title="Pyxel Jump")    #  (width , height)
        pyxel.load("../assets/jump_game.pyxres")

        self.score = 0
        # 左上が(0,0) 右上が(160,0)で、左下が(0,120) 右下が(160,120) = (x, y)
        self.player_x = 72
        self.player_y = -16 # 最初は表示範囲より上に配置される 16x16 の画像
        self.player_dy = 0
        self.is_alive = True

        self.far_cloud = [(-10, 75), (40, 65), (90, 60)]    # 遠景は下部座標
        self.near_cloud = [(10, 25), (70, 35), (120, 15)]   # 近景は上部座標

        # リスト内包記述で、後ろに記述した for 文で生成した値を前のリストに代入して使う
        # また pyxel.rndi は  rndi(a, b) a 以上 b 以下のランダムな整数を返す
        # ex. floor は x, y, 真/偽 = is_alive の3つの要素を持つ3行のList x は固定値、y は乱整数
        self.floor = [(i * 60, pyxel.rndi(8, 104), True) for i in range(4)]
        self.fruit = [
            (i * 60, pyxel.rndi(0, 104), pyxel.rndi(0, 2), True) for i in range(4)
        ]

        # pyxel.playm(0, loop=True) # BGM 演奏
        pyxel.run(self.update, self.draw)

    def update(self):
        # return テスト用
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()

        self.update_player()

        # enumerate はリストのインデックスも取得できる
        for i, v in enumerate(self.floor):
            # 引数の前の * はタプル型変数としてやり取りされる変数であること
            self.floor[i] = self.update_floor(*v)   # x, y, is_alive の要素が self.floor リストに入る

        for i, v in enumerate(self.fruit):
            self.fruit[i] = self.update_fruit(*v)   # 上記同様、に加えて fruit の種類も加わる

    def update_player(self):
        if pyxel.btn(pyxel.KEY_LEFT) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_LEFT):
            self.player_x = max(self.player_x - 2, 0)   # self.player_x-2 か 0 か大き方を返す:0 以下にならない
        if pyxel.btn(pyxel.KEY_RIGHT) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT):
            self.player_x = min(self.player_x + 2, pyxel.width - 16)    # width 160 - 16 より大きくならない

        # floor にぶつかると一時的に dy が -12 になって、-11、-10、-9・・・と上昇速度が落ちる
        # fruit にぶつかると一時的に dy が -8 より小さくなる、大体は上昇する、つまり2段ジャンプのような
        # 1 update毎に落下し、落下幅 dy (Delta Y?)が 1 ずつ大きくなる（加速する）
        self.player_y += self.player_dy # self.player_y = self.player_y + self.player_dy
        self.player_dy = min(self.player_dy + 1, 8) # self.player_dy は 8 より大きくならない

        if self.player_y > pyxel.height:
            if self.is_alive:
                self.is_alive = False   # 生きてる状態で高さ制限以上の位置に行ったら(=落ちたら)、is_alive を False に
                # pyxel.play(3, 5)    # 音の再生、ちなみに曲として再生する場合 pyxel.playm

            if self.player_y > 600: # player_y が 600 以上（落下？）なら初期化 self.is_alive で判断
                self.score = 0
                self.player_x = 72
                self.player_y = -16 # キャラ絵を枠外上部に配置
                self.player_dy = 0
                self.is_alive = True

    def update_floor(self, x, y, is_alive): # x, y は floor の位置[サイズ: 40 x 8], is_alive は floor が壊れていないこと
        if is_alive:
            if (
                self.player_x + 16 >= x # player_x に 16 加えた値が floor 位置 x より大きく
                and self.player_x <= x + 40 # 同、floor 位置 x に 40 加えたより小さい => x - 16 <= _x <= x + 40
                and self.player_y + 16 >= y # player_y に 16 加えた値が y より大きく = 床下方向
                and self.player_y <= y + 8  # floor 位置 y に 8 加えたより小さい => y - 16 <= _y <= 8
                and self.player_dy > 0  # 上下移動している　とこれまで全部の and で floor への当たり判定実施
            ):
                is_alive = False    # floor と player の衝突座標を確認？？
                self.score += 10    # floor 破壊して score が 10 足される
                self.player_dy = -12    # player_dy を -12 上方向に上昇させる
                # pyxel.play(3, 3)
        else:
            y += 6  # 最初生きていなかったら床の位置 y を 6 下方向に落下させる

        x -= 4  # 生死にかかわらず床の位置を左方向に 4 ずらす。最初から床が生きていたらこれだけしかしない。

        if x < -40:
            x += 240    # 表示領域から 40 以上左方向にいたら、右端に移す
            y = pyxel.rndi(8, 104)
            is_alive = True

        return x, y, is_alive

    def update_fruit(self, x, y, kind, is_alive):
        if is_alive and abs(x - self.player_x) < 12 and abs(y - self.player_y) < 12:
            is_alive = False    # fruit と player の衝突座標を確認？？
            self.score += (kind + 1) * 100  # fruit の種類ごとに点数が違う
            self.player_dy = min(self.player_dy, -8)    # つまり最低でも -8 上昇させる
            # pyxel.play(3, 4)

        x -= 2  # 生死に関わらずフルーツの位置を左方向に 2 ずらす

        if x < -40:
            x += 240
            y = pyxel.rndi(0, 104)
            kind = pyxel.rndi(0, 2) # fruitの種類、後は上記同様
            is_alive = True

        return (x, y, kind, is_alive)

    def draw(self):
        pyxel.cls(12)

        # Draw sky 表示位置 0, 88 にイメージバンク 0 の、0, 88 の座標から 160, 32の範囲をコピーする
        pyxel.blt(0, 88, 0, 0, 88, 160, 32) # 空は動かない

        # Draw mountain 同、0, 88 にバンク 0 の、0, 64 の座標から 160, 24をコピーし色12空色を透過
        pyxel.blt(0, 88, 0, 0, 64, 160, 24, 12) # 山も動かない

        # Draw trees
        offset = pyxel.frame_count % 160    # offset は 1 ドットずつ増えて 160 で 0 リセット
        for i in range(2):
            # 表示開始位置をマイナスにして画面が流れるようにしている
            pyxel.blt(i * 160 - offset, 104, 0, 0, 48, 160, 16, 12)

        # Draw clouds、上記同様 // は切り捨て除算
        offset = (pyxel.frame_count // 16) % 160
        for i in range(2):
            for x, y in self.far_cloud: # 雲の遠景は下部、あまり動かない雲
                pyxel.blt(x + i * 160 - offset, y, 0, 64, 32, 32, 8, 12)

        offset = (pyxel.frame_count // 8) % 160
        for i in range(2):
            for x, y in self.near_cloud:    # 雲の近景は上部、良く動く雲
                pyxel.blt(x + i * 160 - offset, y, 0, 0, 32, 56, 8, 12)

        # Draw floors
        for x, y, is_alive in self.floor:
            # x, y の位置にバンク 0 の 0,16 から 40,8 領域をコピー、空色 12 を透過する
            pyxel.blt(x, y, 0, 0, 16, 40, 8, 12)

        # Draw fruits
        for x, y, kind, is_alive in self.fruit:
            if is_alive:
                pyxel.blt(x, y, 0, 32 + kind * 16, 0, 16, 16, 12)

        # Draw player
        pyxel.blt(
            self.player_x,
            self.player_y,
            0,
            16 if self.player_dy > 0 else 0,    # delta y によって jump 中か run 中の絵
            0,
            16,
            16,
            12,
        )

        # Draw score
        s = f"SCORE {self.score:>4}"
        pyxel.text(5, 4, s, 1)
        pyxel.text(4, 4, s, 7)


App()