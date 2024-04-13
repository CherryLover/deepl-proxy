# deep-proxy

## 为什么

很多人其实会有调用 Deepl API 接口翻译的需求，比如使用沉浸式翻译，但是一个 Deepl 的账户每个月只有 50w 字符的免费翻译额度，所以我就尝试自己写了一个代理服务。想法是群里的朋友 @Happy 提供的。

## 如何使用

1. 部署 docker
2. 调用 add 接口添加 Key
3. 将翻译应用修改默认的请求地址改为自己部署的 docker 地址

## 接口

### 添加 Key

其中 auth 是用于翻译请求时的验证，用于区分用户，可以单用户多 key。

```shell
curl -X POST http://yourserver.com/v2/add \
     -H "Content-Type: application/json" \
     -d '{"key": "yourKeyValue", "auth": "yourAuthFileName"}'
```

### 更新用量

docker 中已经内置了每小时更新一次用量情况，另外可通过手动触发更新。

```shell
curl -X GET "https://yourserver.com/v2/usage?auth_key=YOUR_API_KEY"
```

### 翻译

具体翻译 body 的构建参考 deepl，本服务只做转发，不涉及内容。

```shell
curl -X POST http://yourserver.com/v2/translate \
     -H "Authorization: Bearer YOUR_CUSTOM_AUTH_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"text":["Hello, world!"],"target_lang":"DE"}'
```

## 未完待续

- [ ] 可以自定义定时用量查询时间
- [ ] 翻译请求出错重试机制
- [ ] docker 镜像打包发布
