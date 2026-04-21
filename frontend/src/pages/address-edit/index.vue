<template>
  <view class="page-container">
    <view class="address-edit-page">
      <!-- 头部 -->
      <view class="edit-header">
        <text class="edit-title">{{ isEditMode ? '编辑地址' : '添加地址' }}</text>
      </view>

      <!-- 表单 -->
      <view class="form-section">
        <view class="form-group">
          <text class="form-label">收货人</text>
          <input
            v-model="formData.name"
            class="form-input"
            type="text"
            placeholder="请输入收货人姓名"
            maxlength="20"
          />
        </view>

        <view class="form-group">
          <text class="form-label">手机号码</text>
          <input
            v-model="formData.phone"
            class="form-input"
            type="number"
            placeholder="请输入手机号码"
            maxlength="11"
          />
        </view>

        <view class="form-group">
          <text class="form-label">所在地区</text>
          <view class="region-selector" @click="handleShowRegionPicker">
            <text v-if="regionText" class="region-text">{{ regionText }}</text>
            <text v-else class="region-placeholder">请选择省市区</text>
            <text class="region-arrow">›</text>
          </view>
        </view>

        <view class="form-group">
          <text class="form-label">详细地址</text>
          <textarea
            v-model="formData.detail"
            class="form-textarea"
            placeholder="请输入街道、小区、门牌号等详细地址"
            maxlength="100"
            auto-height
          />
        </view>

        <view class="form-group">
          <text class="form-label">邮政编码</text>
          <input
            v-model="formData.postalCode"
            class="form-input"
            type="text"
            placeholder="请输入邮政编码（可选）"
            maxlength="6"
          />
        </view>

        <view class="form-group checkbox-group">
          <view class="checkbox-wrapper" @click="toggleDefault">
            <view class="checkbox" :class="{ 'checked': formData.isDefault }">
              <text v-if="formData.isDefault" class="checkmark">✓</text>
            </view>
            <text class="checkbox-label">设为默认地址</text>
          </view>
        </view>
      </view>

      <!-- 底部操作栏 -->
      <view class="edit-footer">
        <view class="footer-btns">
          <view class="action-btn cancel" @click="handleCancel">
            <text class="action-text">取消</text>
          </view>
          <view class="action-btn save" @click="handleSave">
            <text class="action-text">保存地址</text>
          </view>
        </view>
      </view>

      <!-- 省市区选择器弹窗 -->
      <view v-if="showRegionPicker" class="region-picker-modal" @click="handleHideRegionPicker">
        <view class="region-picker-content" @click.stop>
          <view class="picker-header">
            <text class="picker-cancel" @click="handleHideRegionPicker">取消</text>
            <text class="picker-title">选择省市区</text>
            <text class="picker-confirm" @click="handleConfirmRegion">确定</text>
          </view>
          <view class="picker-body">
            <picker-view :value="pickerIndex" @change="handlePickerChange" class="picker-view">
              <picker-view-column>
                <view v-for="(province, index) in provinces" :key="index" class="picker-item">
                  {{ province.text }}
                </view>
              </picker-view-column>
              <picker-view-column>
                <view v-for="(city, index) in currentCities" :key="index" class="picker-item">
                  {{ city.text }}
                </view>
              </picker-view-column>
              <picker-view-column>
                <view v-for="(district, index) in currentDistricts" :key="index" class="picker-item">
                  {{ district.text }}
                </view>
              </picker-view-column>
            </picker-view>
          </view>
        </view>
      </view>

      <!-- 加载状态 -->
      <view v-if="isLoading" class="loading-overlay">
        <text class="loading-text">加载中...</text>
      </view>

      <view v-if="error" class="error-overlay">
        <text class="error-text">{{ error }}</text>
        <view class="retry-btn" @click="handleRetry">
          <text class="retry-text">重试</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { addressApi } from '../../utils/api/address.api'

// 表单数据结构
interface AddressFormData {
  name: string
  phone: string
  province: string
  city: string
  district: string
  detail: string
  postalCode?: string
  isDefault: boolean
}

const formData = ref<AddressFormData>({
  name: '',
  phone: '',
  province: '',
  city: '',
  district: '',
  detail: '',
  postalCode: '',
  isDefault: false
})

const isEditMode = ref(false)
const addressId = ref<string | null>(null)
const isLoading = ref(false)
const error = ref<string | null>(null)
const showRegionPicker = ref(false)
const pickerIndex = ref([0, 0, 0]) // [省索引, 市索引, 区索引]

// 省市区数据（简化版）
const provinces = ref([
  { text: '北京市', cities: [
    { text: '北京市', districts: ['东城区', '西城区', '朝阳区', '海淀区', '丰台区', '石景山区'] }
  ]},
  { text: '上海市', cities: [
    { text: '上海市', districts: ['黄浦区', '徐汇区', '长宁区', '静安区', '普陀区', '虹口区'] }
  ]},
  { text: '广东省', cities: [
    { text: '广州市', districts: ['天河区', '越秀区', '海珠区', '荔湾区', '白云区', '黄埔区'] },
    { text: '深圳市', districts: ['福田区', '南山区', '罗湖区', '宝安区', '龙岗区', '盐田区'] }
  ]},
  { text: '浙江省', cities: [
    { text: '杭州市', districts: ['上城区', '下城区', '江干区', '拱墅区', '西湖区', '滨江区'] },
    { text: '宁波市', districts: ['海曙区', '江北区', '北仑区', '镇海区', '鄞州区', '奉化区'] }
  ]},
  { text: '江苏省', cities: [
    { text: '南京市', districts: ['玄武区', '秦淮区', '建邺区', '鼓楼区', '浦口区', '栖霞区'] },
    { text: '苏州市', districts: ['姑苏区', '虎丘区', '吴中区', '相城区', '吴江区', '工业园区'] }
  ]}
])

// 计算属性：当前选中的城市列表
const currentCities = computed(() => {
  const provinceIdx = pickerIndex.value[0]
  if (provinceIdx >= 0 && provinceIdx < provinces.value.length) {
    return provinces.value[provinceIdx].cities
  }
  return []
})

// 计算属性：当前选中的区列表
const currentDistricts = computed(() => {
  const provinceIdx = pickerIndex.value[0]
  const cityIdx = pickerIndex.value[1]

  if (provinceIdx >= 0 && provinceIdx < provinces.value.length) {
    const cities = provinces.value[provinceIdx].cities
    if (cityIdx >= 0 && cityIdx < cities.length) {
      return cities[cityIdx].districts
    }
  }
  return []
})

// 计算属性：显示选中的地区文本
const regionText = computed(() => {
  const { province, city, district } = formData.value
  if (province && city && district) {
    return `${province} ${city} ${district}`
  }
  return ''
})

// 计算属性：显示选中的地区文本
const regionText = computed(() => {
  const { province, city, district } = formData.value
  if (province && city && district) {
    return `${province} ${city} ${district}`
  }
  return ''
})

// 页面加载处理
onLoad((options) => {
  const id = options.id
  if (id) {
    isEditMode.value = true
    addressId.value = id
    fetchAddress(id)
  }
})

// 获取地址详情
const fetchAddress = async (id: string) => {
  isLoading.value = true
  error.value = null

  try {
    const response = await addressApi.getAddress(id)
    if (response.success && response.data.address) {
      const address = response.data.address
      formData.value = {
        name: address.name,
        phone: address.phone,
        province: address.province,
        city: address.city,
        district: address.district,
        detail: address.detail,
        postalCode: address.postalCode || '',
        isDefault: address.isDefault
      }
    } else {
      throw new Error(response.message || '获取地址详情失败')
    }
  } catch (err: any) {
    error.value = err.message || '获取地址详情失败'
    console.error('获取地址详情失败:', err)
  } finally {
    isLoading.value = false
  }
}

// 显示省市区选择器
const handleShowRegionPicker = () => {
  showRegionPicker.value = true
}

// 隐藏省市区选择器
const handleHideRegionPicker = () => {
  showRegionPicker.value = false
}

// 处理picker选择变化
const handlePickerChange = (e: any) => {
  const value = e.detail.value
  pickerIndex.value = value

  // 如果省份或城市变化，重置下级索引
  if (value[0] !== pickerIndex.value[0]) {
    pickerIndex.value = [value[0], 0, 0]
  } else if (value[1] !== pickerIndex.value[1]) {
    pickerIndex.value = [value[0], value[1], 0]
  }
}

// 确认地区选择
const handleConfirmRegion = () => {
  const provinceIdx = pickerIndex.value[0]
  const cityIdx = pickerIndex.value[1]
  const districtIdx = pickerIndex.value[2]

  if (provinceIdx >= 0 && provinceIdx < provinces.value.length) {
    const province = provinces.value[provinceIdx]
    formData.value.province = province.text

    if (cityIdx >= 0 && cityIdx < province.cities.length) {
      const city = province.cities[cityIdx]
      formData.value.city = city.text

      if (districtIdx >= 0 && districtIdx < city.districts.length) {
        formData.value.district = city.districts[districtIdx]
      }
    }
  }

  showRegionPicker.value = false
}

// 切换默认地址
const toggleDefault = () => {
  formData.value.isDefault = !formData.value.isDefault
}

// 验证表单
const validateForm = (): boolean => {
  const data = formData.value

  if (!data.name.trim()) {
    uni.showToast({
      title: '请输入收货人姓名',
      icon: 'none'
    })
    return false
  }

  if (!data.phone.trim()) {
    uni.showToast({
      title: '请输入手机号码',
      icon: 'none'
    })
    return false
  }

  // 简单的手机号验证
  const phoneRegex = /^1[3-9]\d{9}$/
  if (!phoneRegex.test(data.phone)) {
    uni.showToast({
      title: '请输入正确的手机号码',
      icon: 'none'
    })
    return false
  }

  if (!data.province || !data.city || !data.district) {
    uni.showToast({
      title: '请选择所在地区',
      icon: 'none'
    })
    return false
  }

  if (!data.detail.trim()) {
    uni.showToast({
      title: '请输入详细地址',
      icon: 'none'
    })
    return false
  }

  return true
}

// 保存地址
const handleSave = async () => {
  if (!validateForm()) {
    return
  }

  isLoading.value = true
  error.value = null

  try {
    if (isEditMode.value && addressId.value) {
      // 更新地址
      await addressApi.updateAddress(addressId.value, formData.value)
      uni.showToast({
        title: '地址更新成功',
        icon: 'success'
      })
    } else {
      // 创建地址
      await addressApi.createAddress(formData.value)
      uni.showToast({
        title: '地址添加成功',
        icon: 'success'
      })
    }

    // 延迟返回，让用户看到成功提示
    setTimeout(() => {
      uni.navigateBack()
    }, 1500)
  } catch (err: any) {
    error.value = err.message || '保存地址失败'
    uni.showToast({
      title: err.message || '保存地址失败',
      icon: 'none'
    })
  } finally {
    isLoading.value = false
  }
}

// 取消编辑
const handleCancel = () => {
  uni.navigateBack()
}

// 重试
const handleRetry = () => {
  error.value = null
  if (addressId.value) {
    fetchAddress(addressId.value)
  }
}

onMounted(() => {
  // 页面初始化逻辑
})
</script>

<style lang="scss" scoped>
@import '../../styles/variables.scss';

.address-edit-page {
  padding-bottom: 120rpx; /* 为底部操作栏留空间 */
}

.edit-header {
  padding: $spacing-lg $spacing-md;
  background-color: $color-white;
  border-bottom: 1px solid $color-border;

  .edit-title {
    font-size: $font-size-xl;
    font-weight: 500;
    color: $color-text-primary;
  }
}

.form-section {
  padding: $spacing-md;
  background-color: $color-white;
  margin: $spacing-md;
  border-radius: $border-radius-lg;
}

.form-group {
  margin-bottom: $spacing-lg;
  padding-bottom: $spacing-md;
  border-bottom: 1px solid $color-border;

  &:last-child {
    margin-bottom: 0;
    padding-bottom: 0;
    border-bottom: none;
  }

  &.checkbox-group {
    border-bottom: none;
    padding: $spacing-md 0;
  }
}

.form-label {
  display: block;
  font-size: $font-size-md;
  font-weight: 400;
  color: $color-text-primary;
  margin-bottom: $spacing-sm;
}

.form-input {
  width: 100%;
  font-size: $font-size-md;
  color: $color-text-primary;
  padding: $spacing-sm 0;
  border: none;
  outline: none;

  &::placeholder {
    color: $color-text-secondary;
  }
}

.region-selector {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: $spacing-sm 0;
  cursor: pointer;

  .region-text {
    font-size: $font-size-md;
    font-weight: 400;
    color: $color-text-primary;
  }

  .region-placeholder {
    font-size: $font-size-md;
    font-weight: 300;
    color: $color-text-secondary;
  }

  .region-arrow {
    font-size: $font-size-xl;
    color: $color-text-secondary;
    transform: rotate(90deg);
  }
}

.form-textarea {
  width: 100%;
  min-height: 120rpx;
  font-size: $font-size-md;
  color: $color-text-primary;
  padding: $spacing-sm 0;
  border: none;
  outline: none;
  resize: none;

  &::placeholder {
    color: $color-text-tertiary;
  }
}

.checkbox-wrapper {
  display: flex;
  align-items: center;
  cursor: pointer;
}

.checkbox {
  width: 36rpx;
  height: 36rpx;
  border: 2px solid $color-border;
  border-radius: $border-radius-sm;
  margin-right: $spacing-sm;
  display: flex;
  align-items: center;
  justify-content: center;

  &.checked {
    background-color: $color-primary;
    border-color: $color-primary;
  }
}

.checkmark {
  color: $color-white;
  font-size: $font-size-sm;
  font-weight: bold;
}

.checkbox-label {
  font-size: $font-size-md;
  font-weight: 400;
  color: $color-text-primary;
}

.edit-footer {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background-color: $color-white;
  border-top: 1px solid $color-border;
  padding: $spacing-md;
  z-index: 100;
}

.footer-btns {
  display: flex;
  gap: $spacing-sm;
}

.action-btn {
  flex: 1;
  border-radius: $border-radius-round;
  padding: $spacing-md;
  text-align: center;

  &.cancel {
    background-color: $color-white;
    border: 1px solid $color-border;
  }

  &.save {
    background-color: $color-accent;
  }

  .action-text {
    font-weight: 500;
    font-size: $font-size-md;

    .cancel & {
      color: $color-text-primary;
    }

    .save & {
      color: $color-white;
    }
  }
}

.region-picker-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 1000;
  display: flex;
  align-items: flex-end;
}

.region-picker-content {
  width: 100%;
  background-color: $color-white;
  border-radius: $border-radius-lg $border-radius-lg 0 0;
  max-height: 70vh;
  display: flex;
  flex-direction: column;
}

.picker-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: $spacing-md;
  border-bottom: 1px solid $color-border;
}

.picker-cancel,
.picker-confirm {
  font-size: $font-size-md;
  color: $color-text-secondary;
  padding: $spacing-sm $spacing-md;
}

.picker-title {
  font-size: $font-size-lg;
  font-weight: 500;
  color: $color-text-primary;
}

.picker-body {
  flex: 1;
  overflow: hidden;
}

.picker-view {
  height: 300rpx;
}

.picker-item {
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: $font-size-md;
  color: $color-text-primary;
  height: 60rpx;
}

.loading-overlay,
.error-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(255, 255, 255, 0.9);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 1000;

  .loading-text,
  .error-text {
    font-size: $font-size-lg;
    color: $color-text-secondary;
    margin-bottom: $spacing-md;
  }

  .retry-btn {
    background-color: $color-primary;
    border-radius: $border-radius-round;
    padding: $spacing-sm $spacing-lg;

    .retry-text {
      color: $color-white;
      font-weight: 500;
      font-size: $font-size-md;
    }
  }
}
</style>