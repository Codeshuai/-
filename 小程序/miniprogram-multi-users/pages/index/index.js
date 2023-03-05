//index.js
const app = getApp()

Page({
  data: {
    inputMsg: '', //保存输入框中的内容
    dialogList: [], //保存对话列表
    id : Math.random()
  },

  //输入框内容改变时触发
  onInputMsgChange(event) {
    this.setData({
      inputMsg: event.detail.value
    })
  },

  //发送按钮点击事件
  onSendBtnClick() {
    console.log(this.data.id)
    //显示加载界面
wx.showLoading({  // 显示加载中loading效果 
  title: "加载中",
  mask: true  //开启蒙版遮罩
})

//你要做的事...
    let inputMsg = this.data.inputMsg.trim()
    if (!inputMsg) {
      return
    }

    //将输入内容添加到对话列表中
    let dialogList = app.globalData.dialogList
    dialogList.push({
      type: 'mine',
      content: inputMsg
    })
    this.setData({
      dialogList: dialogList,
      inputMsg: ''
    })

    //向服务器发送数据
    wx.request({
      url: 'http://127.0.0.1:5000/PromptSapper',
      // url: 'https://www.jxselab.com:8001',
      method: 'POST',
      data: {
        id : this.data.id ,
        inputMsg: inputMsg
      },
      success: (res) => {
        //将服务器返回的数据添加到对话列表中
        let dialogList = app.globalData.dialogList
        // if (res.data.Answer === "Nocode") {
        //   dialogList.push({
        //   type: 'other',
        //   content: '请先输入一段代码！'
        //   })}
        // else if (res.data.Answer === "Menu") {
        //     dialogList.push({
        //     type: 'other',
        //     //set the menus here. for example, content: '1.添加注释；\n2.分析功能；\n3.讲解思路；\n4.提取知识；\n5.代码简化\n6.代码改写;\n（输入数字进行查询，0退出）\n(新输入代码覆盖上一段代码）'
        //     content: '1.添加注释；\n2.分析功能；\n3.讲解思路；\n4.关联知识点；\n5.代码优化\n6.用其它方法实现该代码;\n7.代码查错\n（输入数字进行查询，0退出）\n(新输入代码覆盖上一段代码）'
        //     })}
        // else if (res.data.Answer === "Overflow") {
        //   dialogList.push({
        //   type: 'other',
        //   content: '没有这个选项！'
        //   })}
        // else if (res.data.Answer === "Exit") {
        //   dialogList.push({
        //   type: 'other',
        //   content: '再见！您可以输入一段代码唤醒我。'
        //   })}
        // else {
        //   let answer = res.data.Answer.trim().replace(/^\n+/, '')
        //   dialogList.push({
        //   type: 'other',
        //   content: answer
        //   })}
        var answer = res.data.Answer
        if (answer === []) {
          dialogList.push({
          type: 'other',
          content: '没有返回结果'
        })}
        else {
          var reply = ''
          for (var i=0;i<answer.length;i++){
            reply = reply + answer[i]
          }
          dialogList.push({
            type: 'other',
            content: reply
        })}
        this.setData({
          dialogList: dialogList
        })
        //隐藏加载界面
        wx.hideLoading()
      },
      fail: (err) => {
        console.log('请求服务器失败：', err)
        let dialogList = app.globalData.dialogList
        dialogList.push({
          type: 'other',
          content: ('请求服务器失败："'+err.errMsg+'"')
        })
        this.setData({
          dialogList: dialogList
        })
        //隐藏加载界面
        wx.hideLoading({
          title: "请求失败"
        })
      }
    })
  },

  onLoad: function () {
    //设置初始对话列表
    this.setData({
      dialogList: app.globalData.dialogList
    })
  },

  //上拉触底
onReachBottom: function(){
  console.log('触底')
}
})