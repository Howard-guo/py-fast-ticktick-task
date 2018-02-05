# py-fast-ticktick-task
> 快速添加滴答清单(TickTick)任务



## 调用方式
1. 登录  
  ```login <mail> <pwd>```
2. 配置默认项目  
  ```project <projectName>```
3. 创建任务[只包含标题]  
  ```<tasktitle>```
4. 创建任务[标题+内容]  
  ```<tasktitle> <taskcontent>```
5. 创建任务[标题+剪切板内容]  
  ```<tasktitle> #```



## 注意
* 使用到第三方模块[tzlocal][requests][pyperclip], 需要先[pip install <moudleName>]
* 为方便执行，使用[fastTickTickTask.bat]



## 演示
<div align=center><img src="https://github.com/bjc5233/py-fast-ticktick-task/raw/master/resources/demo.gif"/></div>