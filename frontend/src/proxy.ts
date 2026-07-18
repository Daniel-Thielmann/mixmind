import { NextResponse, type NextRequest } from "next/server";

const protectedPaths = ["/dashboard", "/dashboard/:path*"];

export function proxy(request: NextRequest) {
  const { pathname } = request.nextUrl;

  const isProtected = protectedPaths.some((path) => {
    if (path.endsWith(":path*")) {
      return pathname.startsWith(path.replace("/:path*", ""));
    }
    return pathname === path;
  });

  if (isProtected) {
    const sessionCookie = request.cookies.get("better-auth-session");
    if (!sessionCookie) {
      const url = new URL("/", request.url);
      url.searchParams.set("redirect", pathname);
      return NextResponse.redirect(url);
    }
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/dashboard/:path*"],
};
