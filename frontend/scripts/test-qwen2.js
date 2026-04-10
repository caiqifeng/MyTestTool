const axios = require('axios');

const API_KEY = 'sk-beb049926a3942d3988fcb426cd48035';

// 尝试不同的API端点
const endpoints = [
  {
    name: 'OpenAI兼容聊天端点',
    url: 'https://dashscope.aliyun.com/compatible-mode/v1/chat/completions',
    method: 'POST',
    data: {
      model: 'qwen-max',
      messages: [
        {
          role: 'user',
          content: '你好，请用一句话介绍自己。'
        }
      ],
      stream: false
    }
  },
  {
    name: 'DashScope文本生成',
    url: 'https://dashscope.aliyun.com/api/v1/services/aigc/text-generation/generation',
    method: 'POST',
    data: {
      model: 'qwen-max',
      input: {
        messages: [
          {
            role: 'user',
            content: '你好，请用一句话介绍自己。'
          }
        ]
      }
    }
  },
  {
    name: 'DashScope简单文本生成',
    url: 'https://dashscope.aliyun.com/api/v1/services/aigc/text-generation/generation',
    method: 'POST',
    data: {
      model: 'qwen-max',
      input: {
        prompt: '你好，请用一句话介绍自己。'
      }
    }
  }
];

// 尝试不同的认证头格式
const authHeaders = [
  {
    name: 'Bearer令牌',
    header: `Bearer ${API_KEY}`
  },
  {
    name: '阿里云格式',
    header: API_KEY
  },
  {
    name: 'Authorization头',
    header: `Bearer ${API_KEY}`,
    extraHeaders: {
      'X-DashScope-API-Key': API_KEY
    }
  }
];

async function testEndpoint(endpoint, authHeader) {
  console.log(`\n测试: ${endpoint.name}`);
  console.log(`使用认证: ${authHeader.name}`);
  console.log(`URL: ${endpoint.url}`);

  const headers = {
    'Content-Type': 'application/json'
  };

  // 设置认证头
  if (authHeader.name.includes('Bearer')) {
    headers['Authorization'] = authHeader.header;
  } else {
    headers['Authorization'] = authHeader.header;
  }

  // 添加额外头
  if (authHeader.extraHeaders) {
    Object.assign(headers, authHeader.extraHeaders);
  }

  try {
    const response = await axios({
      method: endpoint.method,
      url: endpoint.url,
      data: endpoint.data,
      headers: headers,
      timeout: 15000
    });

    console.log(`状态码: ${response.status}`);

    if (response.data) {
      // 简化输出
      const data = response.data;
      if (data.choices && data.choices[0] && data.choices[0].message) {
        console.log(`回复: ${data.choices[0].message.content}`);
      } else if (data.output && data.output.text) {
        console.log(`回复: ${data.output.text}`);
      } else if (data.output && data.output.choices && data.output.choices[0] && data.output.choices[0].message) {
        console.log(`回复: ${data.output.choices[0].message.content}`);
      } else {
        console.log('响应数据:', JSON.stringify(data, null, 2).substring(0, 500) + '...');
      }
    }

    return { success: true, response: response.data };
  } catch (error) {
    console.error(`错误: ${error.message}`);
    if (error.response) {
      console.error(`状态码: ${error.response.status}`);
      if (error.response.data) {
        const errorData = typeof error.response.data === 'string'
          ? error.response.data
          : JSON.stringify(error.response.data);
        console.error(`错误响应: ${errorData.substring(0, 300)}...`);
      }
    }
    return { success: false, error: error.message };
  }
}

async function main() {
  console.log('开始测试通义千问API端点...');
  console.log('API密钥:', API_KEY.substring(0, 10) + '...');

  let foundWorkingEndpoint = false;

  for (const endpoint of endpoints) {
    for (const authHeader of authHeaders) {
      const result = await testEndpoint(endpoint, authHeader);

      if (result.success) {
        console.log(`\n✅ 找到可用的端点和认证方式: ${endpoint.name} + ${authHeader.name}`);
        foundWorkingEndpoint = true;
        // 不再继续测试其他组合
        break;
      }

      // 等待一下避免请求过快
      await new Promise(resolve => setTimeout(resolve, 1000));
    }

    if (foundWorkingEndpoint) {
      break;
    }
  }

  if (!foundWorkingEndpoint) {
    console.log('\n❌ 所有端点测试都失败了。');
    console.log('可能的原因:');
    console.log('1. API密钥无效或已过期');
    console.log('2. 网络无法访问阿里云服务');
    console.log('3. 需要开通相应服务权限');
    console.log('4. API端点已变更');

    console.log('\n建议:');
    console.log('1. 登录阿里云控制台检查API密钥状态');
    console.log('2. 检查是否开通了通义千问API服务');
    console.log('3. 查看阿里云DashScope文档获取最新API端点');
  } else {
    console.log('\n✅ API测试成功，可以继续使用。');
  }
}

main().catch(console.error);