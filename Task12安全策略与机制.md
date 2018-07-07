# Web安全性防护策略
##### 说明：该文档基于MatriXay和Acunetix等安全测试工具的测试报告。
## 一、漏洞级别
&emsp;&emsp;紧急、高危、中危、低危、信息。前三种级别的漏洞对网站的危害较大。
## 二、漏洞类型：（漏洞级别）
- 跨站点脚本（XSS）（紧急）
- 框架注入（高危）
- 链接注入（高危）
- CSRF攻击
- 跨域Flash文件访问资源（中危）
- 启用了不安全的HTTP方法（中危）
- 会话Cookie中缺少HttpOnly属性（低危）
- 敏感文件、测试文件（低危）
- 服务器版本泄露（低危）
## 三、漏洞的描述与防御
1. 跨站点脚本（XSS）
- 描述：恶意攻击者往Web页面里插入恶意Script代码，当用户浏览该页之时，嵌入其中Web里面的Script代码会被执行，从而达到恶意攻击用户的目的。
 
- 防御：避免XSS攻击的方法有很多，比如过滤敏感字符、将敏感字符转义等。实际项目中采用了OWASP的一个开源的项目AntiSamy来彻底解决XSS攻击问题。AntiSamy是一个可以确保用户输入的HTML、CSS、JavaScript符合规范的API。它确保了用户无法在HTML中提交恶意代码，而这些恶意代码通常被输入到个人资料、评论等会被服务端存储的数据中。  
2. 框架注入
- 描述：攻击者有可能注入含有恶意内容的  frame 或 iframe 标记。如果用户不够谨慎，就有可能浏览该标记，却意识不到自己会离开原始站点而进入恶意的站点。之后，攻击者便可以诱导用户再次登录，然后获取其登录凭证。
- 防御：过滤客户端提交的危险字符，客户端提交方式包含GET、POST、COOKIE、User-Agent、Referer、Accept-Language等。建议过滤出所有以下字符：
```xml
           |（竖线符号）
           & （& 符号）
           ;（分号）
           $（美元符号）
           %（百分比符号）
           @（at 符号）
           '（单引号）
           "（引号）
           \'（反斜杠转义单引号）
           \"（反斜杠转义引号）
           <>（尖括号）
           ()（括号）
           +（加号）
           CR（回车符，ASCII 0x0d）
           LF（换行，ASCII 0x0a）
           ,（逗号）
           \（反斜杠）
```
3. 链接注入
- 描述：“链接注入”是修改站点内容的行为，其方式为将外部站点的 URL 嵌入其中，或将有易受攻击的站点中的脚本 的 URL 嵌入其中。将 URL 嵌入易受攻击的站点中，攻击者便能够以它为平台来启动对其他站点的攻击，以及攻击这个易受攻击的站点本身。
- 防御：同框架注入。
4. CSRF攻击
- 描述：CSRF（Cross-site request forgery跨站请求伪造，也被称为“one click attack”或者session riding，通常缩写为CSRF或者XSRF，是一种对网站的恶意利用。尽管听起来像跨站脚本（XSS），但它与XSS非常不同，并且攻击方式几乎相左。XSS利用站点内的信任用户，而CSRF则通过伪装来自受信任用户的请求来利用受信任的网站。与XSS攻击相比，CSRF攻击往往不大流行（因此对其进行防范的资源也相当稀少）和难以防范，所以被认为比XSS更具危险性。
- 防御：表单中添加校验token，该token不保存在cookie中。即：由于CSRF的本质在于攻击者欺骗用户去访问自己设置的地址，所以如果要求在访问敏感数据请求时，要求用户浏览器提供不保存在cookie中，并且攻击者无法伪造的数据作为校验，那么攻击者就无法再执行CSRF攻击。这种数据通常是表单中的一个数据项。服务器将其生成并附加在表单中，其内容是一个伪乱数。当客户端通过表单提交请求时，这个伪乱数也一并提交上去以供校验。正常的访问时，客户端浏览器能够正确得到并传回这个伪乱数，而通过CSRF传来的欺骗性攻击中，攻击者无从事先得知这个伪乱数的值，服务器端就会因为校验token的值为空或者错误，拒绝这个可疑请求。
 
5. 跨域Flash文件访问资源
- 描述：Web页面资源是否能从不同域的Flash应用程序进行访问。
- 防御：修改根目录crossdomain.xml文件 例:
```xml
<allow-access-from domain="*.eduyun.cn" to-ports="*"/>
```
6. 启用了不安全的HTTP方法
- 描述：HTTP1.0定义了三种请求方法： GET, POST 和 HEAD方法；HTTP1.1新增了五种请求方法：OPTIONS, PUT, DELETE, TRACE 和 CONNECT 方法。这些方法对可以对web服务的上传、删除、修改等操作，从而对服务产生威胁。
- 防御：两种方法：1 WebDAV有权限控制 2 屏蔽上述新增方法。一般在不需要上述HTTP1.1新增方法的情况下。常用第二种方法。
&emsp;&emsp;第二种方法又分为两种办法，1是修改web服务的web.xml，2是修改tomcat的web.xml,这样对tomcat中所有服务都有效。
示例：
```xml
   <security-constraint>
    <web-resource-collection>
        <web-resource-name>fortune</web-resource-name>
        <url-pattern>/*</url-pattern>
        <http-method>PUT</http-method>
        <http-method>DELETE</http-method>
        <http-method>HEAD</http-method>
        <http-method>OPTIONS</http-method>
        <http-method>TRACE</http-method>
    </web-resource-collection>
    <auth-constraint></auth-constraint></security-constraint>
```
7. cookie中缺少HttpOnly属性
- 描述：应用程序测试过程中，检测到所测试的Web应用程序设置了不含“HttpOnly”属性的会话cookie。有可能被客户端恶意脚本访问，造成信息泄露。
- 防御：对于要依赖于cookie验证的web服务来说，HttpOnly cookies是一个解决方案，在支持HttpOnly cookies的浏览器中（IE6以上，FF3.0以上），javascript是无法读取和修改HttpOnly cookies，或许这样可让网站用户验证更加安全。示例： cookie.setHttpOnly(true);
 
8. 敏感文件、测试文件（低危）
- 描述：Web应用程序显露了某些文件名称，此信息可以帮助攻击者对站点进一步的攻击。比如根目录下的测试文件，像某些test.jsp、a.jsp 等等。
- 防御：不需要保留的，应该删除掉。如果确实需要，应该修改成更复杂的命名。
9. 服务器版本泄露。
- 描述：某些报错、404可能会泄露服务器的版本信息，从而有可能会提供一些信息给攻击者，造成信息不安全的情况。
- 防御：404,500等页面，以及所有的提示找不到的页面或者方法，都应该屏蔽，跳转到相应的报错提示页面。注意配置tomcat的404页。   
## 四、提示
&emsp;&emsp;为了web服务避免安全攻击，紧急、高危、中危级别的漏洞应该及时修复。另外对于版本特别老旧的js，jquery,以及服务器，最好更换到更高的版本，以防安全隐患。对于一些敏感信息，如用户名，密码，email地址不要出现在url中。
