# GiftPedia Vercel Deployment Guide

## 🚀 **VERCEL ENVIRONMENT VARIABLES**

### **✅ **Required Environment Variables**

#### **🔑 API Keys**
```bash
# Gemini AI API Key (Required for AI recommendations)
GEMINI_API_KEY=your_gemini_api_key_here

# Amazon API Credentials (Required for product data)
AMAZON_ACCESS_KEY=your_amazon_access_key
AMAZON_SECRET_KEY=your_amazon_secret_key
AMAZON_ASSOCIATE_TAG=giftpedia-20

# Database Connection (Optional for production)
DATABASE_URL=postgresql://username:password@host:port/database
```

#### **🔧 Configuration**
```bash
# Environment Settings
NODE_ENV=production
NEXT_PUBLIC_API_URL=https://your-domain.vercel.app
NEXT_PUBLIC_APP_NAME=GiftPedia

# Currency and Localization
NEXT_PUBLIC_CURRENCY=INR
NEXT_PUBLIC_LOCALE=en-IN

# Analytics (Optional)
GOOGLE_ANALYTICS_ID=GA-XXXXXXXXX
```

#### **🛡️ Security**
```bash
# JWT Secret (for user authentication)
JWT_SECRET=your_jwt_secret_here

# CORS Settings
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Rate Limiting
RATE_LIMIT_MAX=100
RATE_LIMIT_WINDOW=900000
```

---

## 📱 **DEPLOYMENT STEPS**

### **✅ **Step 1: Connect to Vercel**
1. **Install Vercel CLI**: `npm i -g vercel`
2. **Login**: `vercel login`
3. **Link Project**: `vercel link`

### **✅ **Step 2: Configure Environment Variables**
1. **Go to Vercel Dashboard**: [https://vercel.com/dashboard](https://vercel.com/dashboard)
2. **Select your project**
3. **Go to Settings → Environment Variables**
4. **Add the variables above**

### **✅ **Step 3: Deploy**
```bash
# Deploy to Vercel
vercel --prod

# Or use GitHub integration
git push origin main
```

---

## 🔧 **VERCEL CONFIGURATION**

### **✅ **vercel.json**
```json
{
  "version": 2,
  "name": "giftpedia",
  "builds": [
    {
      "src": "package.json",
      "use": "@vercel/static-build",
      "config": {
        "distDir": "public"
      }
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "/vercel-app.html"
    }
  ],
  "env": {
    "NODE_ENV": "production"
  }
}
```

### **✅ **package.json**
```json
{
  "name": "giftpedia",
  "version": "1.0.0",
  "scripts": {
    "build": "echo 'Build complete'",
    "start": "python -m http.server 3000"
  },
  "dependencies": {},
  "engines": {
    "node": ">=14.0.0"
  }
}
```

---

## 🌐 **DEPLOYMENT OPTIONS**

### **✅ **Option 1: Static Site Deployment**
1. **Use**: `vercel-app.html` as main file
2. **Pros**: Fast, free, simple
3. **Cons**: Limited backend functionality

### **✅ **Option 2: Full-Stack Deployment**
1. **Use**: Backend API + Frontend
2. **Pros**: Full functionality
3. **Cons**: Requires serverless functions

### **✅ **Option 3: Hybrid Deployment**
1. **Frontend**: Vercel static site
2. **Backend**: Separate API deployment
3. **Pros**: Best of both worlds
4. **Cons**: More complex setup

---

## 📊 **ENVIRONMENT VARIABLE SETUP**

### **✅ **Get Gemini API Key**
1. **Go to**: [Google AI Studio](https://aistudio.google.com/)
2. **Create API key**
3. **Copy key**: Add to Vercel environment variables

### **✅ **Get Amazon API Keys**
1. **Go to**: [Amazon Associates](https://affiliate-program.amazon.com/)
2. **Sign up for affiliate program**
3. **Create API credentials**
4. **Add to Vercel environment variables**

### **✅ **Database Setup (Optional)**
1. **Choose**: PostgreSQL provider (Supabase, Neon, etc.)
2. **Create database**
3. **Get connection string**
4. **Add to Vercel environment variables

---

## 🚀 **DEPLOYMENT COMMANDS**

### **✅ **Quick Deploy**
```bash
# Install Vercel CLI
npm i -g vercel

# Login to Vercel
vercel login

# Deploy project
vercel --prod
```

### **✅ **GitHub Integration**
```bash
# Push to GitHub (auto-deploy)
git add .
git commit -m "Deploy to Vercel"
git push origin main
```

### **✅ **Custom Domain**
```bash
# Add custom domain
vercel domains add yourdomain.com
```

---

## 📱 **AFTER DEPLOYMENT**

### **✅ **Your URL**
After deployment, you'll get:
```
https://giftpedia.vercel.app
```
or your custom domain.

### **✅ **Test the Deployment**
1. **Visit your URL**
2. **Test all features**
3. **Check mobile responsiveness**
4. **Verify environment variables**

---

## 🔧 **TROUBLESHOOTING**

### **❌ **Common Issues**

#### **Issue 1: Environment Variables Not Working**
- **Solution**: Check Vercel dashboard settings
- **Verify**: Variable names match exactly

#### **Issue 2: API Calls Failing**
- **Solution**: Verify API keys are correct
- **Check**: Network requests in browser console

#### **Issue 3: Build Fails**
- **Solution**: Check package.json dependencies
- **Verify**: Node version compatibility

#### **Issue 4: Static Assets Not Loading**
- **Solution**: Check file paths in vercel.json
- **Verify**: Routes configuration

---

## 📞 **SUPPORT**

### **✅ **Vercel Resources**
- [Vercel Documentation](https://vercel.com/docs)
- [Environment Variables Guide](https://vercel.com/docs/concepts/projects/environment-variables)
- [Static Site Deployment](https://vercel.com/docs/concepts/static-sites)

### **✅ **GiftPedia Support**
- GitHub Issues: https://github.com/Ajay-Kingpin/GiftPedia/issues
- Documentation: Available in repository

---

## 🎉 **READY TO DEPLOY**

### **✅ **What's Ready**
- **Vercel Configuration**: ✅ Complete setup
- **Environment Variables**: ✅ All required variables listed
- **Deployment Files**: ✅ vercel.json, package.json
- **Static App**: ✅ vercel-app.html ready

### **✅ **Next Steps**
1. **Set up environment variables** in Vercel dashboard
2. **Deploy to Vercel** using the commands above
3. **Test the deployment** and share the link
4. **Monitor performance** and optimize as needed

---

## 🌐 **SHARING YOUR DEPLOYMENT**

### **✅ **Shareable Link**
After deployment:
```
https://giftpedia.vercel.app
```

### **✅ **Stakeholder Email**
```
Subject: GiftPedia - Live Demo on Vercel

Dear [Stakeholder Name],

I'm excited to share our live GiftPedia demo deployed on Vercel!

🔗 Live Demo: https://giftpedia.vercel.app

Key Features:
• AI-powered gift recommendations
• Professional stakeholder interface
• Mobile-responsive design
• Real-time analytics dashboard
• Production-ready performance

The platform showcases our complete AI-powered gift discovery solution with enterprise-grade features.

Best regards,
[Your Name]
GiftPedia Team
```

---

**🚀 Your GiftPedia platform is ready for Vercel deployment!**

**🔗 Set up environment variables and deploy to get your shareable stakeholder link!**
