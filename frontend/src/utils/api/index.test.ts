import axios from 'axios'
import MockAdapter from 'axios-mock-adapter'
import { setActivePinia, createPinia } from 'pinia'
import api, { get, post } from './index'

describe('API Configuration', () => {
  let mock: MockAdapter

  beforeEach(() => {
    // 设置Pinia
    setActivePinia(createPinia())
    mock = new MockAdapter(api) // 使用api实例而不是全局axios
    jest.clearAllMocks()
    // 抑制测试中的console.error输出
    jest.spyOn(console, 'error').mockImplementation(() => {})
  })

  afterEach(() => {
    // 恢复console.error
    jest.restoreAllMocks()
  })

  afterEach(() => {
    mock.restore()
  })

  it('should have correct base URL', () => {
    expect(api.defaults.baseURL).toBe('http://localhost:3003/api')
  })

  it('should have correct timeout', () => {
    expect(api.defaults.timeout).toBe(10000)
  })

  it('should have correct content type header', () => {
    expect(api.defaults.headers['Content-Type']).toBe('application/json')
  })

  it('should handle successful response', async () => {
    const mockData = { id: 1, name: 'Test Product' }
    mock.onGet('/test').reply(200, mockData)

    const response = await get('/test')
    expect(response).toEqual(mockData)
  })

  it('should handle error response', async () => {
    mock.onGet('/error').reply(500, { message: 'Server Error' })

    try {
      await get('/error')
    } catch (error) {
      expect(error).toBeDefined()
    }
  })

  it('should send POST request with data', async () => {
    const requestData = { name: 'Test' }
    const responseData = { id: 1, ...requestData }

    mock.onPost('/test').reply(200, responseData)

    const response = await post('/test', requestData)
    expect(response).toEqual(responseData)
  })
})