# Next.js ke liye base image
FROM node:18

# Working directory set karna
WORKDIR /frontend-app

# Dependencies ko copy karna
COPY package*.json ./

# Dependencies install karna
RUN npm install

# Application code ko copy karna
COPY . .

# Next.js build karna
# RUN npm run build

EXPOSE 3000
# Next.js application ko run karna
CMD ["npm", "run","dev"]
