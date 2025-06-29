import requests
import math
import json
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import threading
from io import BytesIO
from PIL import Image, ImageTk
import datetime
import base64

class HoverButton(ttk.Button):
    """带有悬停效果的按钮"""
    def __init__(self, master=None, style=None, **kwargs):
        super().__init__(master, cursor="hand2", **kwargs)
        self.style = style or ttk.Style()
        self.original_bg = self.style.lookup('TButton', 'background')
        self.hover_bg = '#2980b9'  # 悬停时的背景色
        
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_click)
        self.bind("<ButtonRelease-1>", self._on_release)
        
    def _on_enter(self, event):
        self.state(['active'])
        
    def _on_leave(self, event):
        self.state(['!active'])
        
    def _on_click(self, event):
        self.state(['pressed'])
        
    def _on_release(self, event):
        self.after(100, lambda: self.state(['!pressed']))

class LoadingAnimation:
    """加载动画组件"""
    def __init__(self, master, x, y, size=20, color="#3498db"):
        self.master = master
        self.x = x
        self.y = y
        self.size = size
        self.color = color
        self.canvas = tk.Canvas(master, width=size*3, height=size*3, bg=master["bg"], highlightthickness=0)
        self.canvas.place(x=x, y=y)
        self.dots = []
        self.active = False
        
        # 创建点
        for i in range(8):
            angle = 2 * math.pi * i / 8
            x = size + size * 0.7 * math.cos(angle)
            y = size + size * 0.7 * math.sin(angle)
            self.dots.append(self.canvas.create_oval(
                x-size/6, y-size/6, x+size/6, y+size/6, 
                fill=color, outline=""
            ))
    
    def start(self):
        """开始动画"""
        self.active = True
        self._animate()
        
    def stop(self):
        """停止动画"""
        self.active = False
        if hasattr(self, '_anim_id'):
            self.master.after_cancel(self._anim_id)
        self.canvas.place_forget()
        
    def _animate(self, frame=0):
        """动画帧更新"""
        if not self.active:
            return
            
        for i, dot in enumerate(self.dots):
            # 计算每个点的透明度
            alpha = (i - frame) % 8
            alpha = 1 - alpha / 8
            color = self._adjust_alpha(self.color, alpha)
            self.canvas.itemconfig(dot, fill=color)
            
        self._anim_id = self.master.after(100, lambda: self._animate((frame+1)%8))
        
    def _adjust_alpha(self, color, alpha):
        """调整颜色透明度"""
        rgb = self.master.winfo_rgb(color)
        r = int(rgb[0]/256)
        g = int(rgb[1]/256)
        b = int(rgb[2]/256)
        intensity = int(255 * alpha)
        return f"#{r:02x}{g:02x}{b:02x}"

class HypixelStatsApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Hypixel 玩家数据查询工具 v3.4")
        self.root.geometry("790x900")
        
        # 添加主题设置
        self.style = ttk.Style()
        self.style.theme_use('clam')  # 使用clam主题作为基础
        
        # 自定义样式
        self.style.configure('TButton', font=('微软雅黑', 10), background='#3498db', foreground='white')
        self.style.map('TButton', 
                      background=[('active', '#2980b9'), ('pressed', '#1f618d')],
                      foreground=[('active', 'white'), ('pressed', 'white')])
        self.style.configure('TFrame', background='#f5f5f5')
        self.style.configure('TLabel', background='#f5f5f5', font=('微软雅黑', 10))
        self.style.configure('TEntry', font=('Consolas', 10))
        
        # 设置窗口背景色
        self.root.configure(bg='#f5f5f5')
        
        # 添加加载动画
        self.loading_anim = LoadingAnimation(self.root, 390, 450)
        
        self.skin_img = None
        self.cape_img = None
        
        # 播放入场动画
        self.play_entrance_animation()

    def play_entrance_animation(self):
        """应用启动入场动画"""
        # 隐藏所有组件
        for widget in self.root.winfo_children():
            widget.pack_forget()
        
        # 创建动画画布
        canvas = tk.Canvas(self.root, width=790, height=900, bg="#f5f5f5", highlightthickness=0)
        canvas.pack(fill=tk.BOTH, expand=True)
        
        # 创建标题文本
        title = canvas.create_text(395, 450, text="Hypixel 玩家数据查询工具", 
                                 font=("微软雅黑", 24, "bold"), fill="#3498db")
        
        version = canvas.create_text(395, 490, text="v3.4", 
                                   font=("微软雅黑", 12), fill="#7f8c8d")
        
        # 创建一个简单的加载动画
        dots = []
        for i in range(5):
            x = 395 - 40 + i * 20
            dot = canvas.create_oval(x-5, 530-5, x+5, 530+5, fill="#3498db", outline="")
            dots.append(dot)
        
        # 动画帧函数
        def animate_dot(dot_idx=0, frame=0):
            # 重置所有点的大小
            for i, dot in enumerate(dots):
                size = 5 if i != dot_idx else 8
                x = 395 - 40 + i * 20
                canvas.coords(dot, x-size, 530-size, x+size, 530+size)
            
            # 下一帧
            if frame < 10:  # 每个点动画10帧
                self.root.after(50, lambda: animate_dot(dot_idx, frame+1))
            elif dot_idx < len(dots)-1:  # 移动到下一个点
                self.root.after(50, lambda: animate_dot(dot_idx+1, 0))
            else:  # 动画结束，显示应用
                fade_out()
        
        # 淡出动画
        def fade_out():
            # 渐变隐藏画布
            for i in range(10):
                alpha = 1 - i/10
                # 修改透明度...这里简化处理
                canvas.itemconfig(title, fill=f"#{int(52*(1-alpha)):02x}{int(152*(1-alpha)):02x}{int(219*(1-alpha)):02x}")
                for dot in dots:
                    canvas.itemconfig(dot, fill=f"#{int(52*(1-alpha)):02x}{int(152*(1-alpha)):02x}{int(219*(1-alpha)):02x}")
                self.root.update()
                self.root.after(50)
            
            # 移除画布，显示实际界面
            canvas.destroy()
            
            # 重新显示所有组件
            main_frame = ttk.Frame(self.root)
            main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            self.setup_ui_components(main_frame)  # 将原来setup_ui方法的内容移到这个方法
        
        # 开始动画
        animate_dot()

    # ---------- 界面初始化 ----------
    def setup_ui_components(self, main_frame):
        # 输入区域卡片
        input_card = ttk.Frame(main_frame, style='Card.TFrame')
        input_card.pack(fill=tk.X, pady=5, padx=5, ipady=10)
        
        # 自定义卡片样式
        self.style.configure('Card.TFrame', background='white', relief=tk.RAISED)
        
        input_frame = ttk.Frame(input_card)
        input_frame.pack(fill=tk.X, padx=15, pady=10)
        
        ttk.Label(input_frame, text="API 密钥:").pack(side=tk.LEFT)
        self.api_key_entry = ttk.Entry(input_frame, width=50)
        self.api_key_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(input_frame, text="玩家 ID:").pack(side=tk.LEFT, padx=(10,0))
        self.player_entry = ttk.Entry(input_frame, width=25)
        self.player_entry.pack(side=tk.LEFT)
        
        # 修复：传递样式实例给HoverButton
        self.search_btn = HoverButton(input_frame, text="查询", command=self.start_search, style=self.style)
        self.search_btn.pack(side=tk.LEFT, padx=10)
        
        # 结果显示卡片
        result_card = ttk.Frame(main_frame, style='Card.TFrame')
        result_card.pack(fill=tk.BOTH, expand=True, pady=5, padx=5)
        
        result_frame = ttk.Frame(result_card)
        result_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # 数据面板
        self.data_panel = scrolledtext.ScrolledText(
            result_frame, 
            wrap=tk.WORD,
            font=("Consolas", 20),
            width=60,
            bg="#ffffff",  # 白色背景
            relief=tk.FLAT,  # 扁平外观
            padx=10,  # 内边距
            pady=10,
            bd=1  # 边框宽度
        )
        self.data_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 自定义滚动条样式
        self.style.layout("Vertical.TScrollbar", 
                         [('Vertical.Scrollbar.trough',
                           {'children': [('Vertical.Scrollbar.thumb', 
                                          {'expand': '1', 'sticky': 'nswe'})],
                            'sticky': 'ns'})])
        self.style.configure("Vertical.TScrollbar", 
                            background="#cbd5e0", 
                            troughcolor="#e2e8f0", 
                            width=16,
                            arrowsize=16)
        
        # 图像面板
        img_frame = ttk.Frame(result_frame)
        img_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10)
        
        ttk.Label(img_frame, text="玩家皮肤").pack()
        self.skin_label = ttk.Label(img_frame)
        self.skin_label.pack()
        self.skin_label.bind("<Button-3>", self.save_image)
        
        ttk.Label(img_frame, text="玩家披风", padding=(0,10)).pack()
        self.cape_label = ttk.Label(img_frame)
        self.cape_label.pack()
        self.cape_label.bind("<Button-3>", self.save_image)
        
        # 状态栏
        self.status_bar = ttk.Label(self.root, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def setup_ui(self):
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.setup_ui_components(main_frame)

    # ---------- 核心功能 ----------
    def start_search(self):
        api_key = self.api_key_entry.get().strip()
        player_name = self.player_entry.get().strip()
        
        if not api_key:
            messagebox.showwarning("警告", "请输入有效的API密钥")
            return
        if not player_name:
            messagebox.showwarning("警告", "请输入玩家ID")
            return
            
        self.search_btn.config(state=tk.DISABLED)
        self.animate_search_button()  # 添加动画效果
        self.animate_status_bar("正在查询数据...", highlight=False)
        self.loading_anim.start()  # 启动加载动画
        threading.Thread(target=lambda: self.fetch_data(api_key, player_name)).start()

    def animate_search_button(self):
        """搜索按钮动画效果"""
        original_text = self.search_btn["text"]
        dots = [".", "..", "..."]
        
        def update_text(i=0):
            if self.search_btn["state"] == tk.DISABLED:
                self.search_btn["text"] = f"查询中{dots[i%3]}"
                self.search_btn._animation_id = self.root.after(300, lambda: update_text(i+1))
            else:
                self.search_btn["text"] = original_text
                
        update_text()

    def animate_status_bar(self, text, highlight=True):
        """状态栏动画效果"""
        original_bg = self.status_bar["background"]
        highlight_bg = "#3498db"  # 高亮背景色
        
        self.status_bar.config(text=text)
        
        if highlight:
            # 创建闪烁效果
            def flash(count=0):
                if count >= 6:  # 闪烁3次
                    self.status_bar.config(background=original_bg)
                    return
                
                new_bg = highlight_bg if count % 2 == 0 else original_bg
                self.status_bar.config(background=new_bg)
                self.root.after(200, lambda: flash(count + 1))
                
            flash()
        else:
            # 创建淡出效果
            self.status_bar.config(background=highlight_bg)
            self.root.after(1000, lambda: self.status_bar.config(background=original_bg))

    def fetch_data(self, api_key, player_name):
        try:
            uuid, error = self.get_uuid(player_name)
            if error: 
                raise Exception(error)
            
            hypixel_data = {}
            skin_data = {}
            
            # 多线程获取数据
            def get_hypixel():
                nonlocal hypixel_data
                data, err = self.get_hypixel_data(api_key, uuid)
                if err: 
                    raise Exception(err)
                hypixel_data = data
                
            def get_skin():
                nonlocal skin_data
                skin_data = self.get_skin_data(uuid)
            
            t1 = threading.Thread(target=get_hypixel)
            t2 = threading.Thread(target=get_skin)
            t1.start()
            t2.start()
            t1.join()
            t2.join()
            
            processed_data = self.process_data(hypixel_data, uuid, skin_data)
            self.root.after(0, self.display_results, processed_data)
            self.root.after(0, self.update_images, skin_data)
            
        except Exception as e:
            self.root.after(0, self.show_error, str(e))
        finally:
            self.root.after(0, self.reset_ui)

    # ---------- 数据处理方法 ----------
    def get_uuid(self, player_name):
        """获取玩家UUID"""
        try:
            response = requests.get(
                f"https://api.mojang.com/users/profiles/minecraft/{player_name}",
                timeout=10
            )
            if response.status_code == 204:
                return None, "玩家不存在"
            data = response.json()
            return data.get("id"), None
        except Exception as e:
            return None, f"获取UUID失败: {str(e)}"

    def get_hypixel_data(self, api_key, uuid):
        """获取Hypixel数据"""
        try:
            response = requests.get(
                f"https://api.hypixel.net/player?key={api_key}&uuid={uuid}",
                timeout=15
            )
            data = response.json()
            if not data.get("success"):
                return None, data.get("cause", "未知API错误")
            return data.get("player"), None
        except Exception as e:
            return None, f"API请求失败: {str(e)}"

    def process_data(self, data, uuid, skin_data):
        """整合处理所有数据"""
        return {
            "UUID": uuid,
            "最后登录": self.format_timestamp(data.get("lastLogin")),
            "首次登录": self.format_timestamp(data.get("firstLogin")),
            "基础信息": {
                "显示名称": data.get("displayname"),
                "等级": self.calculate_level(data.get("networkExp", 0)),
                "社交点数": data.get("karma", 0),
                "当前披风": "有" if skin_data.get("cape") else "无"
            },
            "社交": {
                "好友数量": len(data.get("friends", [])),
                "公会": self.get_guild_info(data)
            },
            "游戏数据": {
                "床战争": self.process_bedwars(data.get("stats", {}).get("Bedwars", {})),
                "决斗模式": self.process_duels(data.get("stats", {}).get("Duels", {})),
                "空岛战争": self.process_skywars(data.get("stats", {}).get("SkyWars", {}))
            }
        }

    def process_duels(self, stats):
        """处理决斗模式数据"""
        modes = {
            'bridge_duel': "搭桥决斗",
            'uhc_duel': "UHC决斗",
            'sw_duel': "空岛战争决斗",
            'classic_duel': "经典决斗",
            'op_duel': "超强装备决斗",
            'parkour_eight_duel': "八人跑酷",
            'mw_duel': "超级战墙决斗",
            'bow_duel': "弓箭对决",
            'blitz_duel': "闪电决斗",
            'sumo_duel': "相扑对决",
            'boxing_duel': "拳击对决",
            'skywars_two_v_two': "双人空岛"
        }

        duel_data = {
            "总统计": {
                "总胜场": stats.get("wins", 0),
                "总击杀": stats.get("kills", 0),
                "总死亡": stats.get("deaths", 0),
                "总KD": self.calculate_kd(stats.get("kills", 0), stats.get("deaths", 0)),
                "当前连胜": stats.get("current_winstreak", 0),
                "最高连胜": stats.get("best_overall_winstreak", 0)
            }
        }

        for mode_key, mode_name in modes.items():
            duel_data[mode_name] = {
                "胜场": stats.get(f"{mode_key}_wins", 0),
                "击杀": stats.get(f"{mode_key}_kills", 0),
                "死亡": stats.get(f"{mode_key}_deaths", 0),
                "KD": self.calculate_kd(
                    stats.get(f"{mode_key}_kills", 0),
                    stats.get(f"{mode_key}_deaths", 0)
                ),
                "当前连胜": stats.get(f"{mode_key}_winstreak", 0),
                "最高连胜": stats.get(f"{mode_key}_best_winstreak", 0)
            }

        if 'parkour_eight_duel' in modes:
            duel_data["八人跑酷"].update({
                "最快记录": f"{stats.get('parkour_eight_duel_best_time', 0):.2f}秒",
                "平均时间": f"{stats.get('parkour_eight_duel_average_time', 0):.2f}秒"
            })

        return duel_data

    # ---------- 辅助方法 ----------
    def get_skin_data(self, uuid):
        """获取皮肤数据"""
        try:
            profile = requests.get(
                f"https://sessionserver.mojang.com/session/minecraft/profile/{uuid}",
                timeout=10
            ).json()
            
            for prop in profile.get("properties", []):
                if prop.get("name") == "textures":
                    decoded = base64.b64decode(prop.get("value", ""))
                    textures = json.loads(decoded).get("textures", {})
                    return {
                        "skin": textures.get("SKIN", {}).get("url"),
                        "cape": textures.get("CAPE", {}).get("url")
                    }
            return {}
        except Exception as e:
            print(f"皮肤数据获取失败: {str(e)}")
            return {}

    def fade_in_image(self, label, final_image, steps=10):
        """图像淡入效果"""
        if not hasattr(label, 'image') or not label.image:
            label.image = final_image
            label.config(image=final_image)
            return
            
        # 保存最终图像
        label._final_image = final_image
        
        # 创建过渡图像序列
        for i in range(1, steps + 1):
            alpha = i / steps
            
            def show_frame(alpha=alpha):
                if hasattr(label, '_animation_running') and label._animation_running:
                    # 如果动画正在运行，显示混合图像
                    label.config(image=label._final_image)
                    label.image = label._final_image
                    
                if alpha >= 1:
                    label._animation_running = False
                    
            label._animation_running = True
            self.root.after(50 * i, show_frame)

    def update_images(self, skin_data):
        """更新皮肤显示"""
        def load_image(url, label, size, is_skin=True):
            try:
                response = requests.get(url, timeout=10)
                img = Image.open(BytesIO(response.content))
                
                # 处理透明背景
                if img.mode in ('RGBA', 'LA'):
                    bg = Image.new('RGB', img.size, (255,255,255))
                    bg.paste(img, mask=img.split()[-1])
                    img = bg
                
                # 智能缩放
                w, h = img.size
                target_w, target_h = size
                scale = min(target_w/w, target_h/h)
                img = img.resize((int(w*scale), int(h*scale)), Image.Resampling.LANCZOS)
                
                # 皮肤裁剪
                if is_skin and img.height > img.width:
                    img = img.crop((0, 0, img.width, img.height//2))
                
                photo = ImageTk.PhotoImage(img)
                
                # 使用淡入效果
                self.fade_in_image(label, photo)
                
            except Exception as e:
                print(f"图像加载失败: {str(e)}")

        if skin_data.get("skin"):
            self.root.after(0, load_image, skin_data["skin"], self.skin_label, (200, 400), True)
        if skin_data.get("cape"):
            self.root.after(0, load_image, skin_data["cape"], self.cape_label, (200, 100), False)

    def save_image(self, event):
        """保存图像到本地"""
        widget = event.widget
        if hasattr(widget, "image") and widget.image:
            filename = filedialog.asksaveasfilename(
                title="保存图片",
                defaultextension=".png",
                filetypes=[
                    ("PNG文件", "*.png"),
                    ("JPEG文件", "*.jpg"),
                    ("所有文件", "*.*")
                ]
            )
            if filename:
                try:
                    img = widget.image
                    img._PhotoImage__photo.write(filename, format='PNG')
                    self.status_bar.config(text=f"图片已保存至: {filename}")
                except Exception as e:
                    messagebox.showerror("保存失败", 
                        f"保存过程中出现错误:\n{str(e)}\n"
                        "请确认：\n"
                        "1. 文件路径有写入权限\n"
                        "2. 磁盘空间充足\n"
                        "3. 文件未被其他程序占用")

    def display_results(self, data):
        """显示查询结果，带有渐变效果"""
        self.data_panel.delete(1.0, tk.END)
        formatted = json.dumps(data, indent=4, ensure_ascii=False)
        
        # 分段显示文本，创建渐变效果
        def add_text(text, index=0, chunk_size=300):
            if index < len(text):
                end_index = min(index + chunk_size, len(text))
                chunk = text[index:end_index]
                self.data_panel.insert(tk.END, chunk)
                self.data_panel.see(tk.END)
                self.root.update_idletasks()
                self.root.after(30, lambda: add_text(text, end_index, chunk_size))
            else:
                self.animate_status_bar("查询完成", highlight=True)
        
        add_text(formatted)

    def show_error(self, message):
        """显示错误信息"""
        messagebox.showerror("错误", message)
        self.animate_status_bar("查询失败", highlight=True)

    def reset_ui(self):
        """重置界面状态"""
        if hasattr(self.search_btn, '_animation_id'):
            self.root.after_cancel(self.search_btn._animation_id)
        self.search_btn.config(state=tk.NORMAL)
        self.loading_anim.stop()  # 停止加载动画
        self.status_bar.config(text="准备就绪")

    @staticmethod
    def calculate_level(exp):
        """计算玩家等级"""
        if exp >= 14609081:
            return round(200 + (exp - 14609081) / 96000, 2)
        return round((math.sqrt(exp + 15312.5) - 125/math.sqrt(2)) / (25 * math.sqrt(2)), 2)

    @staticmethod
    def calculate_kd(kills, deaths):
        """计算KD值"""
        return round(kills / deaths, 2) if deaths > 0 else kills

    @staticmethod
    def format_timestamp(timestamp):
        """格式化时间戳"""
        if not timestamp:
            return "未知"
        return datetime.datetime.fromtimestamp(timestamp/1000).strftime("%Y-%m-%d %H:%M:%S")

    def get_guild_info(self, data):
        """获取公会信息"""
        if "guild" not in data:
            return "无"
        return f"{data['guild'].get('name')} (等级: {data['guild'].get('guildLevel', 0)})"

    def process_bedwars(self, stats):
        """处理床战争数据"""
        return {
            "等级": stats.get("level", 0),
            "最终击杀": stats.get("final_kills_bedwars", 0),
            "最终死亡": stats.get("final_deaths_bedwars", 0),
            "KD": self.calculate_kd(stats.get("final_kills_bedwars", 0), 
                                  stats.get("final_deaths_bedwars", 0)),
            "胜场": stats.get("wins_bedwars", 0)
        }

    def process_skywars(self, stats):
        """处理空岛战争数据"""
        return {
            "等级": stats.get("level", 0),
            "击杀": stats.get("kills", 0),
            "死亡": stats.get("deaths", 0),
            "KD": self.calculate_kd(stats.get("kills", 0), stats.get("deaths", 0))
        }

if __name__ == "__main__":
    root = tk.Tk()
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except:
        pass
    app = HypixelStatsApp(root)
    root.mainloop()
