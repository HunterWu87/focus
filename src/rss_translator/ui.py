"""UI界面模块"""
import customtkinter as ctk
from typing import Optional, Callable
import webbrowser
from . import config
from .translator import TranslationService
from .rss_reader import RSSReader
import threading

class RSSTranslatorUI:
    def __init__(self):
        """初始化UI"""
        # 设置主题
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # 创建主窗口
        self.root = ctk.CTk()
        self.root.title(f"RSS翻译器 v{config.APP_VERSION}")
        
        # 加载上次的窗口状态
        self.window_state = config.load_window_state()
        
        # 设置初始窗口大小和位置
        try:
            # 先设置一个默认大小
            self.root.geometry(config.DEFAULT_WINDOW_STATE["geometry"])
            
            # 如果有保存的几何信息，尝试恢复
            if self.window_state.get("geometry"):
                self.root.geometry(self.window_state["geometry"])
            
            # 恢复窗口状态（最大化或全屏）
            if self.window_state.get("maximized", False):
                self.root.after(100, lambda: self.root.state('zoomed'))
            elif self.window_state.get("fullscreen", False):
                self.root.after(100, lambda: self.root.attributes('-fullscreen', True))
        except Exception as e:
            print(f"恢复窗口状态时出错: {str(e)}")
            # 出错时使用默认设置
            self.root.geometry(config.DEFAULT_WINDOW_STATE["geometry"])
        
        # 绑定窗口关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        # 初始化服务
        self.translator = TranslationService()
        self.reader = RSSReader(self.translator)
        self.reader.set_status_callback(self.update_sync_status)  # 设置状态回调
        self.reader.set_log_callback(self.append_status_log)      # 设置日志回调
        
        # 创建UI组件
        self.setup_ui()
        
        # 加载RSS源
        self.load_rss_feed()

    def setup_ui(self):
        """设置UI布局"""
        # 创建主分割布局
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 左侧文章列表区域
        self.list_frame = ctk.CTkFrame(self.main_frame)
        self.list_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        
        # 状态指示器框架（保持在左上角）
        self.status_indicator_frame = ctk.CTkFrame(self.list_frame)
        self.status_indicator_frame.pack(fill="x", padx=5, pady=2)
        
        # 状态指示器
        self.status_indicator = ctk.CTkLabel(
            self.status_indicator_frame,
            text="✓ 已同步",
            font=("Arial", 12),
            text_color="green"
        )
        self.status_indicator.pack(side="left", padx=5)
        
        # 文章列表
        self.article_list = ctk.CTkScrollableFrame(
            self.list_frame,
            fg_color="transparent"  # 设置透明背景
        )
        self.article_list.pack(fill="both", expand=True, padx=5, pady=5)
        
        # 文章列表标题使用更优雅的字体
        self.list_label = ctk.CTkLabel(
            self.list_frame, 
            text="文章列表",
            font=("Microsoft YaHei UI", 16, "bold"),  # 使用微软雅黑，大小16
            text_color=("gray10", "gray90")  # 深色/浅色文字
        )
        self.list_label.pack(pady=5)
        
        # 右侧内容区域
        self.content_frame = ctk.CTkFrame(self.main_frame)
        self.content_frame.pack(side="right", fill="both", expand=True, padx=5, pady=5)
        
        # 创建选项卡
        self.tabview = ctk.CTkTabview(self.content_frame)
        self.tabview.pack(fill="both", expand=True, padx=5, pady=5)
        
        # 添加选项卡
        self.tabview.add("文章总结")  # 调整顺序，先添加总结选项卡
        self.tabview.add("文章详情")
        
        # 设置默认选项卡为"文章总结"
        self.tabview.set("文章总结")
        
        # 禁用标签页点击状态标志
        self.is_tab_disabled = False
        
        # 保存原始的tab切换函数
        self._original_tab_func = self.tabview._segmented_button._command
        
        # 重写tab切换函数
        def custom_tab_func(value):
            if not self.is_tab_disabled:
                self._original_tab_func(value)
                
        self.tabview._segmented_button.configure(command=custom_tab_func)
        
        # 文章总结选项卡内容
        self.summary_text = ctk.CTkTextbox(
            self.tabview.tab("文章总结"),
            font=("Microsoft YaHei UI", 16),  # 设置默认字体
            spacing1=6,   # 段落前间距（减小）
            spacing2=6,   # 行间距（增大）
            spacing3=6,   # 段落后间距（减小）
            padx=20,      # 左右边距
            pady=10       # 上下边距
        )
        self.summary_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 文章详情选项卡内容
        self.detail_text = ctk.CTkTextbox(self.tabview.tab("文章详情"))
        self.detail_text.pack(fill="both", expand=True, padx=5, pady=5)
        
        # 初始化打开链接按钮
        self.summary_open_btn = ctk.CTkButton(
            self.tabview.tab("文章总结"),
            text="在浏览器中打开"
        )
        self.summary_open_btn.pack(pady=5)
        
        self.detail_open_btn = ctk.CTkButton(
            self.tabview.tab("文章详情"),
            text="在浏览器中打开"
        )
        self.detail_open_btn.pack(pady=5)
        
        # 右下角状态日志区域
        self.log_frame = ctk.CTkFrame(self.content_frame)
        self.log_frame.pack(side="bottom", fill="x", padx=5, pady=5)
        
        # 状态日志标签
        self.log_label = ctk.CTkLabel(
            self.log_frame,
            text="状态日志",
            font=("Arial", 12, "bold")
        )
        self.log_label.pack(anchor="w", padx=5, pady=(5,0))
        
        # 状态日志文本框
        self.status_log = ctk.CTkTextbox(
            self.log_frame,
            height=120,
            font=("Arial", 11),
            wrap="word"
        )
        self.status_log.pack(fill="x", padx=5, pady=(2, 5))
        self.status_log.configure(state="disabled")
        
        # 底部状态栏
        self.status_bar = ctk.CTkLabel(
            self.root,
            text=f"翻译模型: {config.MODEL_NAME} ({config.MODEL_VERSION})",
            anchor="w"
        )
        self.status_bar.pack(side="bottom", fill="x", padx=10, pady=5)

    def update_sync_status(self, status: str, is_error: bool = False):
        """更新同步状态显示"""
        self.status_indicator.configure(
            text=status,
            text_color="red" if is_error else "green"
        )
        
    def append_status_log(self, message: str):
        """添加状态日志"""
        try:
            self.status_log.configure(state="normal")  # 临时启用编辑
            self.status_log.insert("end", f"{message}\n")
            self.status_log.see("end")  # 滚动到最新内容
            self.status_log.configure(state="disabled")  # 恢复禁用状态
            
            # 强制更新UI
            self.status_log.update()
            self.status_indicator_frame.update()
        except Exception as e:
            print(f"更新状态日志出错: {str(e)}")

    def load_rss_feed(self):
        """加载RSS源内容"""
        try:
            # 清空文章列表
            for widget in self.article_list.winfo_children():
                widget.destroy()
            
            # 更新状态为同步中
            self.update_sync_status("↻ 同步中...")
            
            # 获取RSS内容
            self.reader.fetch_feed()
            
            # 显示文章列表
            for i, (title, translated_title, url) in enumerate(self.reader.articles, 1):
                # 创建文章框架
                article_frame = ctk.CTkFrame(
                    self.article_list,
                    fg_color=("gray85", "gray20"),  # 浅灰/深灰色
                    corner_radius=6  # 圆角程度
                )
                article_frame.pack(fill="x", padx=5, pady=2)
                
                # 创建文章按钮，使用更优雅的样式
                btn = ctk.CTkButton(
                    article_frame,
                    text=f"{i}. {translated_title}",
                    command=lambda u=url, t=title, tt=translated_title: self.show_article(u, t, tt),
                    anchor="w",
                    height=30,
                    fg_color="transparent",  # 透明背景
                    text_color=("gray10", "gray90"),  # 深色/浅色文字
                    hover_color=("gray75", "gray30"),  # 悬停颜色
                    font=("Microsoft YaHei UI", 18),  # 使用微软雅黑，大小12
                    corner_radius=6
                )
                btn.pack(fill="x", padx=2, pady=2)
            
            # 更新状态为已同步
            self.update_sync_status("✓ 已同步")
            
        except Exception as e:
            self.update_sync_status("✗ 同步失败", True)
            self.show_error(f"加载RSS源失败: {str(e)}")

    def show_article(self, url: str, title: str, translated_title: str):
        """显示文章内容"""
        # 清空详情和总结
        self.detail_text.delete("1.0", "end")
        self.summary_text.delete("1.0", "end")
        
        # 设置更大的字体
        self.summary_text.configure(font=("Microsoft YaHei UI", 13))
        self.detail_text.configure(font=("Microsoft YaHei UI", 13))
        
        # 插入标题（使用不同的字体大小）
        title_font = ("Microsoft YaHei UI", 16, "bold")
        self.summary_text.configure(font=title_font)
        self.summary_text.insert("end", "正在生成文章总结...\n")
        
        # 显示详情
        self.detail_text.configure(font=title_font)
        self.detail_text.insert("end", f"标题：{translated_title}\n")
        self.detail_text.insert("end", f"原标题：{title}\n")
        self.detail_text.configure(font=("Microsoft YaHei UI", 13))
        self.detail_text.insert("end", f"链接：{url}\n")
        self.detail_text.insert("end", "\n")
        
        # 更新按钮状态
        self.detail_open_btn.configure(
            command=lambda: webbrowser.open(url),
            state="normal"
        )
        self.summary_open_btn.configure(
            command=lambda: webbrowser.open(url),
            state="disabled",
            text="正在生成总结..."
        )
        
        # 使用线程处理API调用
        thread = threading.Thread(target=self._load_article_summary_thread, args=(url, title, translated_title))
        thread.daemon = True
        thread.start()
    
    def _load_article_summary_thread(self, url: str, title: str, translated_title: str):
        """在线程中处理API调用"""
        try:
            self.append_status_log("\n=== 开始获取文章总结 ===")
            self.append_status_log(f"文章标题: {title}")
            
            # 先检查数据库中是否已有总结
            self.append_status_log("检查数据库中是否存在总结...")
            summary = self.reader.db.get_article_summary(url)
            
            if summary:
                # 如果已有总结，直接使用
                self.append_status_log("✓ 找到已有总结，直接加载")
                self.root.after(0, lambda: self._update_summary_ui(summary, title, translated_title))
                self.root.after(0, self._restore_buttons)
                self.append_status_log("=== 总结加载完成 ===")
                return

            # 如果没有总结，生成新的总结
            self.append_status_log("未找到已有总结，开始生成...")
            self.append_status_log("正在获取文章内容...")
            
            content = self.reader.get_article_content(url)
            if content:
                self.append_status_log("✓ 文章内容获取成功")
                self.append_status_log("正在生成文章总结...")
                
                summary = self.translator.summarize_article(title, content)
                self.append_status_log("✓ 总结生成成功")
                
                # 保存总结到数据库
                self.append_status_log("正在保存总结到数据库...")
                self.reader.db.update_article_summary(url, summary)
                
                # 更新UI
                self.root.after(0, lambda: self._update_summary_ui(summary, title, translated_title))
                self.append_status_log("=== 总结完成 ===")
            else:
                self.append_status_log("✗ 无法获取文章内容")
                self.root.after(0, lambda: self.show_error("无法获取文章内容"))
                self.append_status_log("=== 总结失败 ===")
        except Exception as e:
            self.append_status_log(f"✗ 生成总结失败: {str(e)}")
            self.root.after(0, lambda: self.show_error(f"生成总结失败: {str(e)}"))
            self.append_status_log("=== 总结失败 ===")
        finally:
            # 在主线程中恢复按钮状态
            self.root.after(0, self._restore_buttons)
    
    def _update_summary_ui(self, summary: str, title: str, translated_title: str):
        """在主线程中更新UI"""
        self.summary_text.delete("1.0", "end")
        
        # 使用更大的标题字体
        title_font = ("Microsoft YaHei UI", 24, "bold")  # 主标题字体
        subtitle_font = ("Microsoft YaHei UI", 18)       # 副标题字体
        content_font = ("Microsoft YaHei UI", 16)        # 正文字体
        
        # 插入标题
        self.summary_text.configure(font=title_font)
        self.summary_text.insert("end", f"{translated_title}\n")
        
        # 插入原标题
        self.summary_text.configure(font=subtitle_font)
        self.summary_text.insert("end", f"{title}\n\n")
        
        # 插入"文章总结"标题
        self.summary_text.configure(font=("Microsoft YaHei UI", 20, "bold"))
        self.summary_text.insert("end", "文章总结\n\n")
        
        # 插入总结内容，优化段落排版
        self.summary_text.configure(font=content_font)
        paragraphs = summary.split('\n')
        for i, paragraph in enumerate(paragraphs):
            if paragraph.strip():  # 如果段落不是空的
                # 添加段落缩进
                self.summary_text.insert("end", "    " + paragraph)
                # 只在段落之间添加一个换行
                if i < len(paragraphs) - 1:
                    self.summary_text.insert("end", "\n")
        
        # 滚动到顶部
        self.summary_text.see("1.0")
    
    def _restore_buttons(self):
        """恢复按钮状态"""
        self.detail_open_btn.configure(state="normal")
        self.summary_open_btn.configure(state="normal", text="在浏览器中打开")

    def show_error(self, message: str):
        """显示错误消息"""
        error_window = ctk.CTkToplevel(self.root)
        error_window.title("错误")
        error_window.geometry("400x200")
        
        error_label = ctk.CTkLabel(
            error_window,
            text=message,
            wraplength=350
        )
        error_label.pack(padx=20, pady=20)
        
        ok_button = ctk.CTkButton(
            error_window,
            text="确定",
            command=error_window.destroy
        )
        ok_button.pack(pady=10)

    def get_monitor_info(self):
        """获取所有显示器信息"""
        try:
            import tkinter as tk
            temp_root = tk.Tk()
            temp_root.withdraw()  # 隐藏临时窗口
            
            # 获取主显示器信息
            monitor_info = {
                "x": int(temp_root.winfo_x()),
                "y": int(temp_root.winfo_y()),
                "width": int(temp_root.winfo_screenwidth()),
                "height": int(temp_root.winfo_screenheight())
            }
            
            temp_root.destroy()  # 确保销毁临时窗口
            return monitor_info
        except Exception as e:
            print(f"获取显示器信息失败: {str(e)}")
            return None

    def get_current_monitor_info(self):
        """获取当前窗口所在显示器信息"""
        try:
            return {
                "x": int(self.root.winfo_x()),
                "y": int(self.root.winfo_y()),
                "width": int(self.root.winfo_width()),
                "height": int(self.root.winfo_height())
            }
        except Exception as e:
            print(f"获取当前窗口信息失败: {str(e)}")
            return None

    def _on_closing(self):
        """窗口关闭时保存状态"""
        try:
            # 获取当前窗口状态
            is_maximized = self.root.state() == 'zoomed'  # Windows
            is_fullscreen = self.root.attributes('-fullscreen')
            
            # 如果是最大化或全屏状态，先恢复正常状态以获取正确的geometry
            if is_maximized:
                self.root.state('normal')
            elif is_fullscreen:
                self.root.attributes('-fullscreen', False)
            
            # 获取窗口geometry
            geometry = self.root.geometry()
            
            # 保存状态
            config.save_window_state(
                geometry=geometry,
                maximized=is_maximized,
                fullscreen=is_fullscreen,
                monitor=None  # 暂时不保存显示器信息，避免类型错误
            )
        except Exception as e:
            print(f"保存窗口状态时出错: {str(e)}")
        finally:
            # 销毁窗口
            self.root.destroy()

    def run(self):
        """运行UI程序"""
        self.root.mainloop() 