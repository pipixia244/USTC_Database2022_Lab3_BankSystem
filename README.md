# USTC 2022春 数据库 实验3 模拟银行系统

- 架构：B/S

- 前端：html + js(jquery) + bootstrap (美化)

- 后端：python + flask + pymysql (RESTful API接口) + mysql (数据库)

- 前后端通信：json

- json格式：
  - code：状态码
  - error：错误信息
  - xxx_list：数据信息
  - length：数据长度

- code定义：  
    200: Success  
    400: Unknown error  
    401: Not authorized  
    402: Wrong password  
    403: Forbidden  
    404: Not found  
    600: Some key cannot be empty  
    601: Some key not exist  
    602: SQL execution error  
    603: Some key already exist  
    604: Action not allowed

