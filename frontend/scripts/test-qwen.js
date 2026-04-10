const axios = require('axios');

const API_KEY = 'sk-beb049926a3942d3988fcb426cd48035';
// 尝试阿里云DashScope API端点
const API_URL = 'https://dashscope.aliyun.com/api/v1/services/aigc/text-generation/generation';

async function testTextGeneration() {
  console.log('测试通义千问文本生成API...');

  try {
    const response = await axios.post(
      API_URL,
      {
        model: 'qwen-max', // 或 qwen-plus, qwen-turbo
        input: {
          messages: [
            {
              role: 'user',
              content: '你好，请用一句话介绍自己。'
            }
          ]
        },
        parameters: {
          result_format: 'message'
        }
      },
      {
        headers: {
          'Authorization': `Bearer ${API_KEY}`,
          'Content-Type': 'application/json',
          'X-DashScope-SSE': 'disable'
        },
        timeout: 30000
      }
    );

    console.log('API响应状态:', response.status);
    console.log('API响应数据:', JSON.stringify(response.data, null, 2));

    if (response.data.output && response.data.output.text) {
      console.log('模型回复:', response.data.output.text);
    }

    return { success: true, data: response.data };
  } catch (error) {
    console.error('API调用错误:', error.message);
    if (error.response) {
      console.error('状态码:', error.response.status);
      console.error('响应头:', error.response.headers);
      console.error('响应数据:', JSON.stringify(error.response.data, null, 2));
    }
    return { success: false, error: error.message };
  }
}

async function testImageGeneration() {
  console.log('\n测试图像生成API（如果支持）...');

  // 通义千问可能不支持直接图像生成，但可以尝试万相API
  // 万相（WanX）是阿里的图像生成服务
  const WANX_API_URL = 'https://dashscope.aliyun.com/api/v1/services/aigc/image-generation/generation';

  try {
    const response = await axios.post(
      WANX_API_URL,
      {
        model: 'wanx2.1-image-generation', // 或 wanx-image-generation-v1
        input: {
          prompt: '一个简单的面包图标，扁平化设计，白色背景'
        },
        parameters: {
          size: '1024x1024',
          n: 1
        }
      },
      {
        headers: {
          'Authorization': `Bearer ${API_KEY}`,
          'Content-Type': 'application/json'
        },
        timeout: 30000
      }
    );

    console.log('图像生成API响应状态:', response.status);
    console.log('图像生成API响应数据:', JSON.stringify(response.data, null, 2));

    return { success: true, data: response.data };
  } catch (error) {
    console.error('图像生成API调用错误:', error.message);
    if (error.response) {
      console.error('状态码:', error.response.status);
      console.error('响应数据:', error.response.data ? JSON.stringify(error.response.data, null, 2) : '无数据');
    }
    return { success: false, error: error.message };
  }
}

async function main() {
  console.log('开始测试通义千问API...\n');

  // 先测试文本生成
  const textResult = await testTextGeneration();

  if (textResult.success) {
    console.log('\n文本生成API测试成功！');

    // 如果文本API成功，再测试图像生成
    const imageResult = await testImageGeneration();

    if (imageResult.success) {
      console.log('\n图像生成API测试成功！');
      console.log('可以开始生成面包图标。');
    } else {
      console.log('\n图像生成API测试失败，通义千问可能不支持直接图像生成。');
      console.log('建议使用专门的图像生成模型，如阿里云的万相（WanX）或其他服务。');
    }
  } else {
    console.log('\nAPI密钥或网络连接可能有问题。');
    console.log('请检查：');
    console.log('1. API密钥是否正确');
    console.log('2. 网络是否可以访问阿里云服务');
    console.log('3. 是否已开通相应服务权限');
  }
}

main().catch(console.error);